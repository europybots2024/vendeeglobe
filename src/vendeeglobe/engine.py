# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Dict, List, Optional

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


from . import config
from .core import Location, WeatherForecast
from .graphics import Graphics
from .map import Map
from .player import Player
from .scores import finalize_scores
from .utils import distance_on_surface
from .weather import Weather


class Engine:
    def __init__(
        self,
        players: dict,
        safe: bool = False,
        test: bool = True,
        time_limit: float = 8 * 60,
        seed: int = None,
        start: Optional[Location] = None,
    ):
        self.time_limit = time_limit
        self.start_time = None
        self.safe = safe
        self.test = test

        if not self.test:
            start = None

        self.players = {
            name: Player(team=name, bot=bot, number=i, start=start)
            for i, (name, bot) in enumerate(players.items())
        }
        print(self.players)

        self.map = Map()
        self.weather = Weather(seed=seed)
        self.graphics = Graphics(
            game_map=self.map, weather=self.weather, players=self.players
        )
        self.start_time = time.time()
        self.last_player_update = self.start_time
        self.last_graphics_update = self.start_time
        self.last_time_update = self.start_time
        self.last_forecast_update = self.start_time
        self.players_not_arrived = list(self.players.keys())
        self.forecast = self.weather.get_forecast(0)

        self.set_schedule()
        self.group_counter = 0

    def set_schedule(self):
        times = []
        for player in self.players.values():
            t0 = time.time()
            player.execute_bot(t=0, info=self.get_info(player), safe=self.safe)
            times.append(((time.time() - t0), player))
        ng = 3
        time_groups = {i: [] for i in range(ng)}
        self.player_groups = {i: [] for i in range(ng)}
        for t in sorted(times, key=lambda tup: tup[0], reverse=True):
            ind = np.argmin([sum(g) for g in time_groups.values()])
            time_groups[ind].append(t[0])
            self.player_groups[ind].append(t[1])

    def get_info(self, player: Player) -> Dict[str, float]:
        return {
            "longitude": player.longitude,
            "latitude": player.latitude,
            "heading": player.heading,
            "speed": player.speed,
            "vector": player.get_vector(),
            "forecast": self.forecast,
        }

    def call_player_bots(self, t: float, players: List[Player]):
        for player in players:
            player.execute_bot(t=t, info=self.get_info(player), safe=self.safe)

    def move_players(self, weather: Weather, t: float, dt: float):
        latitudes = np.array([player.latitude for player in self.players.values()])
        longitudes = np.array([player.longitude for player in self.players.values()])
        u, v = weather.get_uv(latitudes, longitudes, np.array([t]))
        for i, player in enumerate([p for p in self.players.values() if not p.arrived]):
            lat, lon = player.get_path(dt, u[i], v[i])
            terrain = self.map.get_terrain(longitudes=lon, latitudes=lat)
            sea_inds = np.where(terrain == 1)[0]
            if len(sea_inds) > 0:
                player.latitude = lat[sea_inds[-1]]
                player.longitude = lon[sea_inds[-1]]
            for checkpoint in player.checkpoints:
                if not checkpoint.reached:
                    d = distance_on_surface(
                        origin=[player.longitude, player.latitude],
                        to=[checkpoint.longitude, checkpoint.latitude],
                    )
                    if d < checkpoint.radius:
                        checkpoint.reached = True
                        print(f"{player.team} reached {checkpoint}")
            dist_to_finish = distance_on_surface(
                origin=[player.longitude, player.latitude],
                to=[config.start.longitude, config.start.latitude],
            )
            if dist_to_finish < config.start.radius and all(
                ch.reached for ch in player.checkpoints
            ):
                player.arrived = True
                self.players_not_arrived.remove(player.team)
                print(f"{player.team} finished!")
                player.score = config.scores.pop(0)
                print("player score:", player.score)

    def shutdown(self):
        finalize_scores(players=self.players, test=self.test)
        self.timer.stop()

    def update(self):
        clock_time = time.time()
        t = clock_time - self.start_time
        if t > self.time_limit:
            self.shutdown()

        if (clock_time - self.last_time_update) > config.time_update_interval:
            self.graphics.update_time(self.time_limit - t)
            self.last_time_update = clock_time

        if (clock_time - self.last_forecast_update) > config.weather_update_interval:
            self.forecast = self.weather.get_forecast(t)
            print(self.forecast.u.shape, self.forecast.v.shape)
            self.last_forecast_update = clock_time

        self.call_player_bots(
            t=t,
            players=self.player_groups[self.group_counter % len(self.player_groups)],
        )
        self.weather.update_wind_tracers(
            t=np.array([t]), dt=config.graphics_update_interval
        )
        self.move_players(self.weather, t=t, dt=config.graphics_update_interval)
        self.graphics.update_wind_tracers(
            self.weather.tracer_lat, self.weather.tracer_lon
        )
        self.graphics.update_player_positions(self.players)
        self.group_counter += 1

        if len(self.players_not_arrived) == 0:
            self.shutdown()

    def run(self):
        self.graphics.window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        pg.exec()
