# SPDX-License-Identifier: BSD-3-Clause

import time
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

from . import config
from .utils import lat_degs_from_length, lon_degs_from_length, wrap


@dataclass(frozen=True)
class WeatherForecast:
    u: np.ndarray
    v: np.ndarray
    du: float
    dv: float
    dt: float

    def get_uv(
        self, lat: np.ndarray, lon: np.ndarray, t: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the wind speed at the given latitude, longitude and time.

        Parameters
        ----------
        lat: np.ndarray
            Latitude in degrees.
        lon: np.ndarray
            Longitude in degrees.
        t: np.ndarray
            Time in hours.
        """
        iv = ((np.asarray(lat) + 90.0) / self.dv).astype(int)
        iu = ((np.asarray(lon) + 180.0) / self.du).astype(int)
        it = ((np.asarray(t) / config.seconds_to_hours) / self.dt).astype(
            int
        )  #  % self.nt
        u = self.u[it, iv, iu]
        v = self.v[it, iv, iu]
        return u, v


class Weather:
    def __init__(self, time_limit: int, seed: Optional[int] = None):
        t0 = time.time()
        print("Generating weather...", end=" ", flush=True)
        rng = np.random.default_rng(seed)

        self.ny = 128
        self.nx = self.ny * 2
        self.nt = int(time_limit / config.weather_update_interval)

        self.dt = config.weather_update_interval  # weather changes every 12 hours

        nseeds = 300  # 350
        sigma = 8

        image = np.zeros([self.nt, self.ny, self.nx])
        dy = self.ny // 6
        xseed = rng.integers(self.nx, size=nseeds)
        yseed = rng.integers(dy, self.ny - dy, size=nseeds)
        tseed = rng.integers(self.nt, size=nseeds)

        image[(tseed, yseed, xseed)] = 10000
        smooth = gaussian_filter(image, sigma=sigma, mode="wrap")
        normed = smooth / smooth.max()

        angle = normed * 360.0
        angle = (angle + 180.0) % 360.0
        angle *= np.pi / 180.0
        self.angle = angle

        self.u = np.cos(angle)
        self.v = np.sin(angle)

        div = np.abs(np.array(sum(np.gradient(normed))))
        speed = (1.0 - div / div.max()) * 75.0
        self.u *= speed
        self.v *= speed

        lat_min = -90
        lat_max = 90
        self.dv = (lat_max - lat_min) / self.ny
        lon_min = -180
        lon_max = 180
        self.du = (lon_max - lon_min) / self.nx

        size = (config.tracer_lifetime, config.ntracers)
        self.tracer_lat = np.random.uniform(-89.9, 89.9, size=size)
        self.tracer_lon = np.random.uniform(-180, 180, size=size)
        self.tracer_colors = np.ones(self.tracer_lat.shape + (4,))
        self.tracer_colors[..., 3] = np.linspace(1, 0, 50).reshape((-1, 1))

        self.number_of_new_tracers = 5
        self.new_tracer_counter = 0

        # Make forecast data
        self.forecast_times = np.arange(
            0, config.forecast_length * 6, config.weather_update_interval
        )
        nf = len(self.forecast_times)

        blurred_u = uniform_filter(self.u, size=30, mode="wrap")
        blurred_v = uniform_filter(self.v, size=30, mode="wrap")
        coeffs_a = np.linspace(0, 1, nf)
        coeffs_b = np.linspace(1, 0, nf)
        shape = self.u.shape + (1,)
        u_r = self.u.reshape(shape)
        v_r = self.v.reshape(shape)
        bu_r = blurred_u.reshape(shape)
        bv_r = blurred_v.reshape(shape)

        self.forecast_u = np.transpose(
            coeffs_b * u_r + coeffs_a * bu_r, axes=[3, 0, 1, 2]
        )
        self.forecast_v = np.transpose(
            coeffs_b * v_r + coeffs_a * bv_r, axes=[3, 0, 1, 2]
        )

        self.u.setflags(write=False)
        self.v.setflags(write=False)
        self.forecast_u.setflags(write=False)
        self.forecast_v.setflags(write=False)
        print(f"done [{time.time() - t0:.2f} s]")

    def get_forecast(self, t: float) -> WeatherForecast:
        t = t + self.forecast_times
        it = (t / self.dt).astype(int) % self.nt
        ik = np.arange(len(t))
        return WeatherForecast(
            u=self.forecast_u[ik, it, ...],
            v=self.forecast_v[ik, it, ...],
            du=self.du,
            dv=self.dv,
            dt=self.dt,
        )

    def get_uv(
        self, lat: np.ndarray, lon: np.ndarray, t: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        iv = ((lat + 90.0) / self.dv).astype(int)
        iu = ((lon + 180.0) / self.du).astype(int)
        it = (t / self.dt).astype(int) % self.nt
        u = self.u[it, iv, iu]
        v = self.v[it, iv, iu]
        return u, v

    def update_wind_tracers(self, t: float, dt: float):
        self.tracer_lat = np.roll(self.tracer_lat, 1, axis=0)
        self.tracer_lon = np.roll(self.tracer_lon, 1, axis=0)

        u, v = self.get_uv(self.tracer_lat[1, :], self.tracer_lon[1, :], t)

        scaling = 1.0
        incr_x = u * dt * scaling
        incr_y = v * dt * scaling
        incr_lon = lon_degs_from_length(incr_x, self.tracer_lat[1, :])
        incr_lat = lat_degs_from_length(incr_y)

        self.tracer_lat[0, :], self.tracer_lon[0, :] = wrap(
            lat=self.tracer_lat[1, :] + incr_lat, lon=self.tracer_lon[1, :] + incr_lon
        )

        # Randomly replace tracers
        new_lat = np.random.uniform(-89.9, 89.9, size=(self.number_of_new_tracers,))
        new_lon = np.random.uniform(-180, 180, size=(self.number_of_new_tracers,))
        istart = self.new_tracer_counter
        iend = self.new_tracer_counter + self.number_of_new_tracers
        self.tracer_lat[0, istart:iend] = new_lat
        self.tracer_lon[0, istart:iend] = new_lon
        self.new_tracer_counter = (
            self.new_tracer_counter + self.number_of_new_tracers
        ) % config.ntracers
