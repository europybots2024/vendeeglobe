# SPDX-License-Identifier: BSD-3-Clause

import os


import numpy as np
from PIL import Image

from . import config


class Map:
    def __init__(self):
        print('Loading world map...', end=' ', flush=True)
        im = Image.open(os.path.join(config.resourcedir, config.map_file))
        self.array = np.array(im.convert('RGBA'))
        img16 = self.array.astype('int16')
        self.sea_array = np.flipud(
            np.where(img16[:, :, 2] > (img16[:, :, 0] + img16[:, :, 1]), 1, 0)
        )
        self.high_contrast_texture = np.array(
            Image.fromarray(np.uint8(self.sea_array * 255)).convert('RGBA')
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
        print('done')

    def get_terrain(self, longitudes, latitudes):
        ilon = ((longitudes + 180.0) / self.dlon).astype(int)
        ilat = ((latitudes + 90.0) / self.dlat).astype(int)
        return self.sea_array[ilat, ilon]
