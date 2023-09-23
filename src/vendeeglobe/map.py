# SPDX-License-Identifier: BSD-3-Clause

import os

import numpy as np
from PIL import Image

from . import config
from . import utils


class Map:
    def __init__(self, width, height):
        im = Image.open(os.path.join(config.resourcedir, config.map_file))
        self.array = np.array(im.convert('RGBA'))
        img16 = self.array.astype('int16')
        self.sea_array = np.where(
            img16[:, :, 2] > (img16[:, :, 0] + img16[:, :, 1]), 1, 0
        )

        self.nlat, self.nlon, _ = self.array.shape
        lat_min = -90
        lat_max = 90
        self.dlat = (lat_max - lat_min) / self.nlat
        lon_min = -180
        lon_max = 180
        self.dlon = (lon_max - lon_min) / self.nlon
        self.lat = np.linspace(
            lat_min + 0.5 * self.dlat, lat_max - 0.5 * self.dlat, self.nlat
        )
        self.lon = np.linspace(
            lon_min + 0.5 * self.dlon, lon_max - 0.5 * self.dlon, self.nlon
        )
        self.lon_grid, self.lat_grid = np.meshgrid(self.lon, self.lat)
        print(self.lat_grid.shape, self.lon_grid.shape)

    def get_terrain(self, longitudes, latitudes):
        ilon = (longitudes / self.dlon).astype(int) + (self.nlon // 2)
        ilat = (latitudes / self.dlat).astype(int) + (self.nlat // 2)
        return self.sea_array[ilat, ilon]

        # self.array = np.load(
        #     os.path.join(config.resourcedir, f'world{config.map_resolution}.npz')
        # )['world']

        # im = Image.open(os.path.join(config.resourcedir, "world.jpg"))
        # self.array = np.array(im.convert('RGBA'))
        # img16 = self.array.astype('int16')
        # self.sea_array = np.where(
        #     img16[:, :, 2] > (img16[:, :, 0] + img16[:, :, 1]), 1, 0
        # )
        # sea = Image.fromarray((self.sea_array.astype(np.uint8)) * 255)
        # sea.save("sea.png")

        # size = (config.tracer_lifetime, config.ntracers)
        # self.tracer_lat = np.random.uniform(-90.0, 90.0, size=size)
        # self.tracer_lon = np.random.uniform(-180, 180, size=size)
        # # self.tracer_lat = np.broadcast_to(
        # #     np.array([48.8566, 40.7128]).reshape((1, -1)), (config.tracer_lifetime, 2)
        # # )
        # # self.tracer_lon = np.broadcast_to(
        # #     np.array([2.3522, -74.0060]).reshape((1, -1)), (config.tracer_lifetime, 2)
        # # )
        # # self.tracer_lat = np.random.uniform(-10.0, 10.0, size=config.ntracers)
        # # self.tracer_lon = np.zeros_like(self.tracer_lat)
        # self.tracer_colors = np.ones(self.tracer_lat.shape + (4,))
        # self.tracer_colors[..., 3] = np.linspace(1, 0, 50).reshape((-1, 1))
        # # self.tracer_colors[..., 3] = 0.5

        # # self.tracer_lon = np.random.uniform(-10, 10, size=config.ntracers)
        # # self.tracer_lat = np.zeros_like(self.tracer_lon)
