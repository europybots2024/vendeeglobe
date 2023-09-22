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
from .player import Player
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
        config.setup(players=players)

        self.time_limit = time_limit
        self.start_time = None

        self.players = {
            name: Player(team=name, score=0, number=i)
            for i, (name, ai) in enumerate(players.items())
        }

        self.app = pg.mkQApp("GLImageItem Example")
        self.map = Map(width=width, height=height)
        self.graphics = Graphics(self.map, players=self.players)
        self.weather = Weather(self.map)
        self.start_time = time.time()

    def move_players(self, weather_map, t, dt):
        # return
        latitudes = np.array([player.latitude for player in self.players.values()])
        longitudes = np.array([player.longitude for player in self.players.values()])
        u, v, n = weather_map.get_uv(latitudes, longitudes, t)
        for i, player in enumerate(self.players.values()):
            player.move(t, dt, u[i], v[i])

    def update(self):
        t = time.time() - self.start_time
        self.map.update_wind_tracers(self.weather, t=t, dt=0.1)
        self.move_players(self.weather, t=t, dt=0.1)
        # for team, player in self.players.items():
        #     player.move()
        self.graphics.update_wind_tracers(self.map.tracer_lat, self.map.tracer_lon)
        self.graphics.update_player_positions(self.players)

    def run(self, N=10000):
        self.graphics.window.show()

        t = QtCore.QTimer()
        t.timeout.connect(self.update)
        t.start(50)

        pg.exec()
