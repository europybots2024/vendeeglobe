# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config


class Weather:
    def __init__(self, world_map):
        # # self.u = ((world_map.lat_grid > 0).astype(float) * 2.0) - 1.0
        # self.u = world_map.lat_grid / np.abs(world_map.lat_grid)
        # self.v = np.zeros_like(self.u)

        x0 = 0.0
        y0 = 0.0
        gamma = 10.0
        r2 = (world_map.lon_grid - x0) ** 2 + (world_map.lat_grid - y0) ** 2
        self.u = gamma * (world_map.lat_grid - y0) / r2
        self.v = -gamma * (world_map.lon_grid - x0) / r2
        # return u, v
