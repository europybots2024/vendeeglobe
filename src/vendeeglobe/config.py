# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path


class Config:
    def __init__(self):
        self.map_resolution = 4096
        self.nlat = self.map_resolution
        self.nlon = 2 * self.map_resolution
        self.map_radius = 6371
        self.resourcedir = Path(__file__).parent / "resources"
        self.ntracers = 10000
