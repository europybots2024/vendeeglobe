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
from .scores import finalize_scores
from .utils import distance_on_surface
from .weather import Weather


class Engine:
    def __init__(
        self,
        players: dict,
        safe=False,
        test=True,
        fps=1,
        time_limit=7 * 60,
        seed=None,
        current_round=0,
        start=None,
    ):
        np.random.seed(seed)
        config.setup(players=players)

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

        for p in self.players.values():
            p.latitude += np.random.uniform(-5.0, 5.0)
            p.longitude += np.random.uniform(-5.0, 5.0)
            for ch in p.checkpoints:
                ch.reached = True

        # self.scores = self.read_scores(players=players, test=test)
        self.app = pg.mkQApp("GLImageItem Example")
        self.map = Map()
        self.weather = Weather()
        self.graphics = Graphics(
            game_map=self.map, weather=self.weather, players=self.players
        )
        self.start_time = time.time()
        self.last_player_update = self.start_time
        self.last_graphics_update = self.start_time
        self.last_time_update = self.start_time
        self.players_not_arrived = list(self.players.keys())

        # self.call_player_bots(t=0)
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

    # def read_scores(self, players: dict, test: bool) -> Dict[str, int]:
    #     scores = {p: 0 for p in players}
    #     fname = "scores.txt"
    #     if os.path.exists(fname) and (not test):
    #         with open(fname, "r") as f:
    #             contents = f.readlines()
    #         for line in contents:
    #             name, score = line.split(":")
    #             scores[name] = int(score.strip())
    #     # else:
    #     #     scores = {p: 0 for p in players}
    #     print("Scores:", scores)
    #     return scores

    # def write_scores(self):
    #     fname = "scores.txt"
    #     with open(fname, "w") as f:
    #         for name, score in self.scores.items():
    #             f.write(f"{name}: {score}\n")
    #     # for i, (name, score) in enumerate(sorted_scores):
    #     #     print(f"{i + 1}. {name}: {score}")

    # def collect_scores(self):
    #     player_groups = {0: [], 1: [], 2: []}
    #     for player in self.players.values():
    #         n = len([ch for ch in player.checkpoints if ch.reached])
    #         player_groups[n].append(player)

    #     start = [config.start['longitude'], config.start['latitude']]

    #     # Players that reached 2 checkpoints
    #     group_players = []
    #     for player in player_groups[2]:
    #         if player.score is None:
    #             dist = distance_on_surface(
    #                 origin=[player.longitude, player.latitude],
    #                 to=start,
    #             )
    #             group_players.append((dist, player))
    #     group_players.sort()
    #     for _, player in group_players:
    #         player.score = config.scores.pop(0) if config.scores else 0
    #     for player in player_groups[2]:
    #         self.scores[player.team] += player.score

    #     # Players that reached 1 checkpoint
    #     group_players = []
    #     for player in player_groups[1]:
    #         for ch in player.checkpoints:
    #             if not ch.reached:
    #                 dist = distance_on_surface(
    #                     origin=[player.longitude, player.latitude],
    #                     to=[ch.longitude, ch.latitude],
    #                 ) + distance_on_surface(
    #                     origin=[ch.longitude, ch.latitude],
    #                     to=start,
    #                 )
    #                 group_players.append((dist, player))
    #     group_players.sort()
    #     for _, player in group_players:
    #         player.score = config.scores.pop(0) if config.scores else 0
    #     for player in player_groups[1]:
    #         self.scores[player.team] += player.score

    #     # Players that reached 0 checkpoints
    #     group_players = []
    #     for player in player_groups[0]:
    #         dists = [
    #             distance_on_surface(
    #                 origin=[player.longitude, player.latitude],
    #                 to=[ch.longitude, ch.latitude],
    #             )
    #             for ch in player.checkpoints
    #         ]
    #         ind = np.argmin(dists)
    #         dist = (
    #             dists[ind]
    #             + distance_on_surface(
    #                 origin=[
    #                     player.checkpoints[0].longitude,
    #                     player.checkpoints[1].latitude,
    #                 ],
    #                 to=[
    #                     player.checkpoints[1].longitude,
    #                     player.checkpoints[1].latitude,
    #                 ],
    #             )
    #             + distance_on_surface(
    #                 origin=[
    #                     player.checkpoints[(ind + 1) % 2].longitude,
    #                     player.checkpoints[(ind + 1) % 2].latitude,
    #                 ],
    #                 to=start,
    #             )
    #         )
    #         group_players.append((dist, player))
    #     group_players.sort()
    #     for _, player in group_players:
    #         player.score = config.scores.pop(0) if config.scores else 0
    #     for player in player_groups[0]:
    #         self.scores[player.team] += player.score

    #     # Print scores
    #     all_scores = [
    #         (p.team, p.score, self.scores[p.team]) for p in self.players.values()
    #     ]
    #     sorted_scores = sorted(all_scores, key=lambda tup: tup[2], reverse=True)
    #     print("Scores:")
    #     for i, (name, score, total) in enumerate(sorted_scores):
    #         print(f"{i + 1}. {name}: {score} ({total})")

    def get_info(self, player):
        return {
            "longitude": player.longitude,
            "latitude": player.latitude,
            "heading": player.heading,
        }

    def call_player_bots(self, t, players):
        for player in players:
            player.execute_bot(t=t, info=self.get_info(player), safe=self.safe)

    def move_players(self, weather, t, dt):
        # return
        latitudes = np.array([player.latitude for player in self.players.values()])
        longitudes = np.array([player.longitude for player in self.players.values()])
        u, v = weather.get_uv(latitudes, longitudes, np.array([t]))
        for i, player in enumerate([p for p in self.players.values() if not p.arrived]):
            lat, lon = player.get_path(t, dt, u[i], v[i])
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
                        # player.score += 1
                        print(f"{player.team} reached {checkpoint}")
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
            dist_to_finish = distance_on_surface(
                origin=[player.longitude, player.latitude],
                to=[config.start['longitude'], config.start['latitude']],
            )
            if dist_to_finish < config.start["radius"] and all(
                ch.reached for ch in player.checkpoints
            ):
                # if not player.arrived:
                player.arrived = True
                self.players_not_arrived.remove(player.team)
                print(f"{player.team} finished!")
                # s = config.scores.pop(0)
                # self.scores[player.team] += s
                player.score = config.scores.pop(0)
                print("player score:", player.score)
                # player.global_score += 1
                # self.scores[player.team] += 1
                # print(self.scores)
                # if len(self.arrived_players) == len(self.players):
                #     self.write_scores()
                #     exit()

    def shutdown(self):
        finalize_scores(players=self.players, test=self.test)
        exit()

    def update(self):
        clock_time = time.time()
        t = clock_time - self.start_time
        if t > self.time_limit:
            self.shutdown()
            # finalize_scores(players=self.players, test=self.test)
            # # sc.write_scores()
            # exit()

        # if (clock_time - self.last_player_update) > config.player_update_interval:
        #     u, v = self.weather.get_forecast(
        #         t=t + np.arange(0, 2 * config.forecast_length, 2)
        #     )
        #     self.call_player_bots(t=t)
        #     self.last_player_update = clock_time
        # if (clock_time - self.last_graphics_update) > config.graphics_update_interval:
        #     self.weather.update_wind_tracers(
        #         t=np.array([t]), dt=config.graphics_update_interval
        #     )
        #     self.move_players(self.weather, t=t, dt=config.graphics_update_interval)
        #     self.graphics.update_wind_tracers(
        #         self.weather.tracer_lat,
        #         self.weather.tracer_lon,
        #         self.weather.tracer_colors,
        #     )
        #     self.graphics.update_player_positions(self.players)

        if (clock_time - self.last_time_update) > config.time_update_interval:
            self.graphics.update_time(self.time_limit - t)
            self.last_time_update = clock_time

        # # TODO: only update forecast when needed
        # u, v = self.weather.get_forecast(
        #     t=t + np.arange(0, 2 * config.forecast_length, 2)
        # )

        self.call_player_bots(
            t=t,
            players=self.player_groups[self.group_counter % len(self.player_groups)],
        )
        self.weather.update_wind_tracers(
            t=np.array([t]), dt=config.graphics_update_interval
        )
        self.move_players(self.weather, t=t, dt=config.graphics_update_interval)
        self.graphics.update_wind_tracers(
            self.weather.tracer_lat,
            self.weather.tracer_lon,
            self.weather.tracer_colors,
        )
        self.graphics.update_player_positions(self.players)
        self.group_counter += 1

        if len(self.players_not_arrived) == 0:
            self.shutdown()

    def run(self):
        self.graphics.window.show()
        # self.graphics.layout.show()

        t = QtCore.QTimer()
        t.timeout.connect(self.update)
        t.start(50)

        pg.exec()
