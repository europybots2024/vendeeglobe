# SPDX-License-Identifier: BSD-3-Clause

import matplotlib as mpl
import numpy as np
from scipy.ndimage import gaussian_filter
from typing import Optional, Tuple

from . import config
from .utils import wrap, lon_degs_from_length, lat_degs_from_length


class Weather:
    def __init__(self, seed: Optional[int] = None):
        rng = np.random.default_rng(seed)

        self.ny = 128
        self.nx = self.ny * 2
        self.nt = self.ny

        # Weather stays constant for 2 player updates: player update every 12 hours
        self.dt = 2.0 * config.player_update_interval

        nseeds = 250
        sigma = 6

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

        self.u = np.cos(angle)
        self.v = np.sin(angle)

        div = np.abs(np.array(sum(np.gradient(normed))))
        speed = (1.0 - div / div.max()) * 10.0
        self.u *= speed
        self.v *= speed

        lat_min = -90
        lat_max = 90
        self.dv = (lat_max - lat_min) / self.ny
        lon_min = -180
        lon_max = 180
        self.du = (lon_max - lon_min) / self.nx

        size = (config.tracer_lifetime, config.ntracers)
        self.tracer_lat = np.random.uniform(-90.0, 90.0, size=size)
        self.tracer_lon = np.random.uniform(-180, 180, size=size)
        self.tracer_colors = np.ones(self.tracer_lat.shape + (4,))
        self.tracer_colors[..., 3] = np.linspace(1, 0, 50).reshape((-1, 1))

        self.tracer_cmap = mpl.colormaps['Reds']
        self.norm = mpl.colors.Normalize()

        self.number_of_new_tracers = 5
        self.new_tracer_counter = 0

    def get_forecast(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        it = (t / self.dt).astype(int) % self.nt
        u = self.u[it, ...]
        v = self.v[it, ...]
        for i in range(len(t)):
            u[i, ...] = gaussian_filter(u[i, ...], sigma=(i + 1) * 2, mode="wrap")
            v[i, ...] = gaussian_filter(v[i, ...], sigma=(i + 1) * 2, mode="wrap")
        return u, v

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

        scaling = 5.0
        incr_lon = u * dt * scaling
        incr_lat = v * dt * scaling
        incr_lon = lon_degs_from_length(incr_lon, self.tracer_lat[1, :])
        incr_lat = lat_degs_from_length(incr_lat)

        self.tracer_lat[0, :], self.tracer_lon[0, :] = wrap(
            lat=self.tracer_lat[1, :] + incr_lat, lon=self.tracer_lon[1, :] + incr_lon
        )

        # Randomly replace tracers
        new_lat = np.random.uniform(-90.0, 90.0, size=(self.number_of_new_tracers,))
        new_lon = np.random.uniform(-180, 180, size=(self.number_of_new_tracers,))
        istart = self.new_tracer_counter
        iend = self.new_tracer_counter + self.number_of_new_tracers
        self.tracer_lat[0, istart:iend] = new_lat
        self.tracer_lon[0, istart:iend] = new_lon
        self.new_tracer_counter = (
            self.new_tracer_counter + self.number_of_new_tracers
        ) % config.ntracers
