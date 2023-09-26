# SPDX-License-Identifier: BSD-3-Clause

from typing import List, Tuple

from pathlib import Path
import matplotlib.pyplot as plt


def _make_colors(num_colors: int) -> List[Tuple[float, ...]]:
    cols = []
    cmap = plt.get_cmap("gist_ncar")
    for i in range(num_colors):
        cols.append(cmap(i / max(num_colors - 1, 1)))
    return cols


class Config:
    def __init__(self):
        self.map_file = "world.jpg"
        # self.map_resolution = 4096
        # self.nlat = self.map_resolution
        # self.nlon = 2 * self.map_resolution
        self.map_radius = 6371
        self.resourcedir = Path(__file__).parent / "resources"
        self.ntracers = 5000
        self.tracer_lifetime = 50
        self.bot_polling_interval = 1.0
        self.start = {'longitude': -4.773949, 'latitude': 48.333422, 'radius': 5.0}
        self.checkpoints = [
            {'latitude': 2.806318, 'longitude': -168.943864, 'radius': 1000.0},
            {'latitude': -15.668984, 'longitude': 77.674694, 'radius': 1000.0},
        ]
        self.scores = {
            1: 25,
            2: 18,
            3: 15,
            4: 12,
            5: 10,
            6: 8,
            7: 6,
            8: 4,
            9: 2,
            10: 1,
        }

    def setup(self, players):
        self.colors = _make_colors(len(players))
