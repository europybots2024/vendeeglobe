# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from scipy.ndimage import gaussian_filter

from . import config


# def make_fluctuations_map(nx, ny, nt):
#     image = np.zeros([nt, ny, nx])
#     nseeds = int((nx * ny * nt) * 20000 / (1920 * 1080 * 1000))
#     nseeds = int((ny / 4) ** 3)
#     xseed = np.random.randint(nx, size=nseeds)
#     yseed = np.random.randint(ny, size=nseeds)
#     tseed = np.random.randint(nt, size=nseeds)
#     image[(tseed, yseed, xseed)] = 10000
#     return gaussian_filter(image, sigma=ny // 16, mode="wrap")


class Weather:
    def __init__(self, world_map):
        # # self.u = ((world_map.lat_grid > 0).astype(float) * 2.0) - 1.0
        # self.u = world_map.lat_grid / np.abs(world_map.lat_grid)
        # self.v = np.zeros_like(self.u)

        # x0 = 0.0
        # y0 = 0.0
        # gamma = 10.0
        # r2 = (world_map.lon_grid - x0) ** 2 + (world_map.lat_grid - y0) ** 2
        # self.u = gamma * (world_map.lat_grid - y0) / r2
        # self.v = -gamma * (world_map.lon_grid - x0) / r2
        # # self.u = np.full_like(world_map.lat_grid, 1.0)
        # # self.v = np.zeros_like(world_map.lon_grid)
        # # return u, v

        self.ny = 128
        self.nx = self.ny * 2
        self.nt = self.ny

        nseeds = 100
        sigma = 10

        image = np.zeros([self.nt, self.ny, self.nx])
        # nseeds = int((self.nx * self.ny * self.nt) * 20000 / (1920 * 1080 * 1000))
        # nseeds = int((self.ny / 4) ** 3)
        dy = self.ny // 3
        xseed = np.random.randint(self.nx, size=nseeds)
        yseed = np.random.randint(self.ny - dy, size=nseeds) + int(0.5 * dy)
        # yseed = np.random.randint(self.ny, size=nseeds)
        tseed = np.random.randint(self.nt, size=nseeds)
        # print(nseeds)

        image[(tseed, yseed, xseed)] = 10000
        smooth = gaussian_filter(image, sigma=sigma, mode="wrap")
        normed = smooth / smooth.max()

        angle = normed * 360.0
        angle = (angle + 180.0) % 360.0
        angle *= np.pi / 180.0
        # angle = 0 * angle
        self.u = np.cos(angle)
        self.v = np.sin(angle)

        div = np.abs(np.array(sum(np.gradient(normed))))
        self.speed = (1.0 - div / div.max()) * 10.0
        # speed = sum(np.gradient(smooth))
        # self.speed = speed / speed.max() * 10.0

        lat_min = -90
        lat_max = 90
        self.dv = (lat_max - lat_min) / self.ny
        lon_min = -180
        lon_max = 180
        self.du = (lon_max - lon_min) / self.nx

    def get_uv(self, lat, lon, t):
        iv = (lat / self.dv).astype(int) + (self.ny // 2)
        iu = (lon / self.du).astype(int) + (self.nx // 2)
        it = int(t % self.nt)

        u = self.u[it, iv, iu]
        v = self.v[it, iv, iu]
        n = self.speed[it, iv, iu]
        # u = 1.0
        # v = 0.0
        # iu = (self.u / self.du).astype(int) + (self.nx // 2)
        # iv = (self.v / self.dv).astype(int) + (self.ny // 2)
        return u, v, n
