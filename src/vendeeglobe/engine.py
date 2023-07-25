# SPDX-License-Identifier: BSD-3-Clause

import importlib
import os
import time
from typing import Dict

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


from . import config
from .graphics import Graphics
from .map import Map
from .weather import Weather


class Engine:
    def __init__(
        self,
        players: dict,
        safe=False,
        width=1200,
        height=900,
        test=True,
        fps=1,
        time_limit=300,
        seed=None,
        current_round=0,
    ):
        np.random.seed(seed)

        self.time_limit = time_limit
        self.start_time = None

        self.app = pg.mkQApp("GLImageItem Example")
        self.map = Map(width=width, height=height)
        self.graphics = Graphics(self.map)
        self.weather = Weather(self.map)

    def update(self):
        self.map.update_wind_tracers(self.weather, dt=2)
        self.graphics.update_wind_tracers(self.map.tracer_lat, self.map.tracer_lon)

    def run(self, N=10000):
        self.graphics.window.show()

        t = QtCore.QTimer()
        t.timeout.connect(self.update)
        t.start(50)

        pg.exec()
