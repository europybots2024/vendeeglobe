# SPDX-License-Identifier: BSD-3-Clause

import os

import numpy as np

from . import config
from . import utils


class Map:
    def __init__(self, width, height):
        lat_min = -90
        lat_max = 90
        self.dlat = (lat_max - lat_min) / config.nlat
        lon_min = -180
        lon_max = 180
        self.dlon = (lon_max - lon_min) / config.nlon
        self.lat = np.linspace(
            lat_min + 0.5 * self.dlat, lat_max - 0.5 * self.dlat, config.nlat
        )
        self.lon = np.linspace(
            lon_min + 0.5 * self.dlon, lon_max - 0.5 * self.dlon, config.nlon
        )
        self.lon_grid, self.lat_grid = np.meshgrid(self.lon, self.lat)

        self.array = np.load(
            os.path.join(config.resourcedir, f'world{config.map_resolution}.npz')
        )['world']

        self.tracer_lat = np.random.uniform(-90.0, 90.0, size=config.ntracers)
        self.tracer_lon = np.random.uniform(-180, 180, size=config.ntracers)

    def update_wind_tracers(self, weather_map, dt):
        lat_inds = (self.tracer_lat / self.dlat).astype(int) + (config.nlat // 2)
        lon_inds = (self.tracer_lon / self.dlon).astype(int) + (config.nlon // 2)
        incr_lon = weather_map.u[lat_inds, lon_inds] * dt
        incr_lat = weather_map.v[lat_inds, lon_inds] * dt
        self.tracer_lat = utils.wrap_lat(self.tracer_lat + incr_lat)
        self.tracer_lon = utils.wrap_lon(self.tracer_lon + incr_lon)
        # self.tracers.geometry.attributes['position'].array = utils.to_xyz(
        #     utils.lon_to_phi(self.tracer_lon), utils.lat_to_theta(self.tracer_lat)
        # )
