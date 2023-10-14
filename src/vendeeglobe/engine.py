# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Dict, List, Optional

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

import datetime


import sys

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QCheckBox,
        QSizePolicy,
        QFrame,
    )
except ImportError:
    from PySide2.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QCheckBox,
        QSizePolicy,
        QFrame,
    )


from . import config
from .core import Location, WeatherForecast
from .graphics import Graphics
from .map import Map
from .player import Player
from .scores import finalize_scores, get_current_scores, get_player_points
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
        self.previous_clock_time = self.start_time
        self.players_not_arrived = list(self.players.keys())
        self.forecast = self.weather.get_forecast(0)
        self.tracers_hidden = False

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
        empty_groups = [i for i, g in time_groups.items() if len(g) == 0]
        for i in empty_groups:
            del self.player_groups[i]

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
                next_lat = lat[sea_inds[-1]]
                next_lon = lon[sea_inds[-1]]
                player.distance_travelled += distance_on_surface(
                    origin=[player.longitude, player.latitude],
                    to=[next_lon, next_lat],
                )
                player.latitude = next_lat
                player.longitude = next_lon
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
                player.score = config.pop_score()
                print("player score:", player.score)

    def shutdown(self):
        finalize_scores(players=self.players, test=self.test)
        self.timer.stop()

    def update(self):
        clock_time = time.time()
        t = clock_time - self.start_time
        dt = (clock_time - self.previous_clock_time) * config.seconds_to_hours
        if t > self.time_limit:
            self.shutdown()

        if (clock_time - self.last_time_update) > config.time_update_interval:
            self.update_scoreboard(self.time_limit - t)
            self.last_time_update = clock_time

        if (clock_time - self.last_forecast_update) > config.weather_update_interval:
            self.forecast = self.weather.get_forecast(t)
            # print(self.forecast.u.shape, self.forecast.v.shape)
            self.last_forecast_update = clock_time

        self.call_player_bots(
            t=t,
            players=self.player_groups[self.group_counter % len(self.player_groups)],
        )
        self.move_players(self.weather, t=t, dt=dt)
        if self.tracer_checkbox.isChecked():
            self.weather.update_wind_tracers(t=np.array([t]), dt=dt)
            self.graphics.update_wind_tracers(
                self.weather.tracer_lat,
                self.weather.tracer_lon,
                reset_colors=self.tracers_hidden,
            )
            self.tracers_hidden = False
        else:
            if not self.tracers_hidden:
                self.graphics.hide_wind_tracers()
                self.tracers_hidden = True
        self.graphics.update_player_positions(self.players)
        self.group_counter += 1

        if len(self.players_not_arrived) == 0:
            self.shutdown()

        self.previous_clock_time = clock_time

    def update_scoreboard(self, t: float):
        time = str(datetime.timedelta(seconds=int(t)))[2:]
        self.time_label.setText(f"Time left: {time} s")

        # current_scores = get_current_scores(self.players)
        status = [
            (
                get_player_points(player),
                player.distance_travelled,
                player.team,
                len([ch for ch in player.checkpoints if ch.reached]),
            )
            for player in self.players.values()
        ]
        for i, (_, dist, team, nch) in enumerate(sorted(status, reverse=True)):
            self.player_boxes[i].setText(f"{i+1}. {team}: {int(dist)} km [{nch}]")

    def run(self):
        # self.graphics.window.show()
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update)
        # self.timer.start(0)
        # pg.exec()

        # app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Vendée Globe")
        window.setGeometry(100, 100, 1280, 720)

        # Create a central widget to hold the two widgets
        central_widget = QWidget()
        window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout(central_widget)

        # Create the first widget with vertical checkboxes
        widget1 = QWidget()
        layout.addWidget(widget1)
        widget1_layout = QVBoxLayout(widget1)
        widget1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget1.setMinimumWidth(int(window.width() * 0.1))

        self.time_label = QLabel("Time left:")
        widget1_layout.addWidget(self.time_label)
        self.tracer_checkbox = QCheckBox("Show wind tracers", checked=True)
        widget1_layout.addWidget(self.tracer_checkbox)
        self.texture_checkbox = QCheckBox("High contrast", checked=False)
        widget1_layout.addWidget(self.texture_checkbox)
        self.texture_checkbox.stateChanged.connect(self.graphics.toggle_texture)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        widget1_layout.addWidget(separator)

        self.player_boxes = {}
        for i in range(len(self.players)):
            # widget1_layout = QHBoxLayout(widget1_layout)
            self.player_boxes[i] = QLabel("")
            widget1_layout.addWidget(self.player_boxes[i])

        layout.addWidget(self.graphics.window)
        self.graphics.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        pg.exec()
        # sys.exit(self.graphics.app.exec_())
