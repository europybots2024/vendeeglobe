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
from .utils import distance
from .weather import Weather


class Engine:
    def __init__(
        self,
        players: dict,
        safe=False,
        test=True,
        fps=1,
        time_limit=300,
        seed=None,
        current_round=0,
        start=None,
    ):
        np.random.seed(seed)
        config.setup(players=players)

        self.time_limit = time_limit
        self.start_time = None
        self.safe = safe

        if not test:
            start = None

        self.players = {
            name: Player(team=name, bot=bot, score=0, number=i, start=start)
            for i, (name, bot) in enumerate(players.items())
        }
        print(self.players)

        self.app = pg.mkQApp("GLImageItem Example")
        self.map = Map()
        self.weather = Weather(self.map)
        self.graphics = Graphics(
            game_map=self.map, weather=self.weather, players=self.players
        )
        self.start_time = time.time()

    def get_info(self, player):
        return {
            "longitude": player.longitude,
            "latitude": player.latitude,
            "heading": player.heading,
        }

    def call_player_bots(self, t, dt):
        for player in self.players.values():
            player.execute_bot(t=t, dt=dt, info=self.get_info(player), safe=self.safe)

    def move_players(self, weather, t, dt):
        # return
        latitudes = np.array([player.latitude for player in self.players.values()])
        longitudes = np.array([player.longitude for player in self.players.values()])
        u, v, n = weather.get_uv(latitudes, longitudes, t)
        for i, player in enumerate(self.players.values()):
            lat, lon = player.get_path(t, dt, u[i], v[i], n[i])
            terrain = self.map.get_terrain(longitudes=lon, latitudes=lat)
            sea_inds = np.where(terrain == 1)[0]
            if len(sea_inds) > 0:
                player.latitude = lat[sea_inds[-1]]
                player.longitude = lon[sea_inds[-1]]
            for checkpoint in self.map.checkpoints:
                if not checkpoint.reached:
                    d = distance()
                    # if utl.check_distance(
                    #     player.latitude,
                    #     player.longitude,
                    #     checkpoint.latitude,
                    #     checkpoint.longitude,
                    #     checkpoint.radius,
                    # ):
                    #     checkpoint.reached = True
                    #     player.score += 1
                    #     print(f"{player.team} reached {checkpoint}")

    def update(self):
        t = time.time() - self.start_time
        dt = 0.1
        self.weather.update_wind_tracers(t=t, dt=dt)
        self.call_player_bots(t=t, dt=dt)
        self.move_players(self.weather, t=t, dt=dt)
        # for team, player in self.players.items():
        #     player.move()
        self.graphics.update_wind_tracers(
            self.weather.tracer_lat, self.weather.tracer_lon
        )
        self.graphics.update_player_positions(self.players)

    def run(self, N=10000):
        self.graphics.window.show()

        t = QtCore.QTimer()
        t.timeout.connect(self.update)
        t.start(50)

        pg.exec()
