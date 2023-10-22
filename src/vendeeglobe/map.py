# SPDX-License-Identifier: BSD-3-Clause

import os
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
from PIL import Image
import time

from . import config


class Map:
    def __init__(self):
        t0 = time.time()
        print('Creating world map...', end=' ', flush=True)
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
        self.sea_array.setflags(write=False)
        print(f'done [{time.time() - t0:.2f} s]')

    def get_terrain(self, longitudes, latitudes):
        ilon = ((longitudes + 180.0) / self.dlon).astype(int)
        ilat = ((latitudes + 90.0) / self.dlat).astype(int)
        return self.sea_array[ilat, ilon]


@dataclass(frozen=True)
class MapProxy:
    array: np.ndarray
    dlat: float
    dlon: float

    def get_inds(
        self, latitude: Union[float, np.ndarray], longitude: Union[float, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        ilat = ((np.asarray(latitude) + 90.0) / self.dlat).astype(int)
        ilon = ((np.asarray(longitude) + 180.0) / self.dlon).astype(int)
        return ilat, ilon

    def get_data(
        self, latitude: Union[float, np.ndarray], longitude: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        ilat, ilon = self.get_inds(latitude, longitude)
        return self.array[ilat, ilon]
