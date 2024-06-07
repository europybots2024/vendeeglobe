# SPDX-License-Identifier: BSD-3-Clause

import datetime
import time
from typing import Any, Dict

import numpy as np


from . import config
from .map import MapData
from .player import Player
from .scores import get_player_points, write_times
from . import utils as ut
from .weather import Weather


class Engine:
    def __init__(
        self,
        pid: int,
        seed: int,
        bots: Dict[str, Any],
        players: Dict[str, Player],
        bot_index_begin: int,
        buffers: dict,
        safe: bool,
        world_map: MapData,
    ):
        self.bot_index_begin = bot_index_begin
        self.bot_index_end = bot_index_begin + len(bots)
        self.buffers = {
            key: ut.array_from_shared_mem(*value) for key, value in buffers.items()
        }
        self.pid = pid
        self.safe = safe
        self.bots = bots
        self.players = players
        self.player_tracks = np.zeros(
            [len(self.players), 2 * config.time_limit * config.fps, 3]
        )
        self.position_counter = 0

        self.map = world_map
        self.weather = Weather(
            self.pid,
            seed,
            weather_u=self.buffers["weather_u"],
            weather_v=self.buffers["weather_v"],
            forecast_u=self.buffers["forecast_u"],
            forecast_v=self.buffers["forecast_v"],
            forecast_t=self.buffers["forecast_t"],
            tracer_positions=self.buffers["tracer_positions"],
        )
        self.buffers["all_shutdown"][self.pid] = False
        self.players_not_arrived = list(self.players.keys())
        self.forecast = self.weather.get_forecast(0)

    def initialize_time(self, start_time: float):
        self.start_time = start_time
        self.last_player_update = self.start_time
        self.last_graphics_update = self.start_time
        self.last_time_update = self.start_time
        self.last_forecast_update = self.start_time
        self.previous_clock_time = self.start_time
        self.update_interval = 1 / config.fps

    def execute_player_bot(self, player, t: float, dt: float):
        instructions = None
        args = {
            "t": t,
            "dt": dt,
            "longitude": player.longitude,
            "latitude": player.latitude,
            "heading": player.heading,
            "speed": player.speed,
            "vector": player.get_vector(),
            "forecast": self.forecast.get_uv,
            "world_map": self.map.get_terrain,
        }
        if self.safe:
            try:
                instructions = self.bots[player.team].run(**args)
            except:  # noqa
                pass
        else:
            instructions = self.bots[player.team].run(**args)
        return instructions

    def call_player_bots(self, t: float, dt: float):
        for player in [p for p in self.players.values() if not p.arrived]:
            if self.safe:
                try:
                    player.execute_bot_instructions(
                        self.execute_player_bot(player=player, t=t, dt=dt)
                    )
                except:  # noqa
                    pass
            else:
                player.execute_bot_instructions(
                    self.execute_player_bot(player=player, t=t, dt=dt)
                )

    def move_players(self, weather: Weather, t: float, dt: float):
        latitudes = np.array([player.latitude for player in self.players.values()])
        longitudes = np.array([player.longitude for player in self.players.values()])
        u, v = weather.get_uv(latitudes, longitudes, np.array([t]))
        for i, player in enumerate(self.players.values()):
            lat, lon = player.get_path(0 if player.arrived else dt, u[i], v[i])
            terrain = self.map.get_terrain(longitudes=lon, latitudes=lat)
            w = np.where(terrain == 0)[0]
            if len(w) > 0:
                ind = max(w[0] - 1, 0)
            else:
                ind = len(terrain) - 1
            if ind > 0:
                next_lat = lat[ind]
                next_lon = lon[ind]
                player.distance_travelled += ut.distance_on_surface(
                    longitude1=player.longitude,
                    latitude1=player.latitude,
                    longitude2=next_lon,
                    latitude2=next_lat,
                )
                player.latitude = next_lat
                player.longitude = next_lon

            if not player.arrived:
                for checkpoint in player.checkpoints:
                    if not checkpoint.reached:
                        d = ut.distance_on_surface(
                            longitude1=player.longitude,
                            latitude1=player.latitude,
                            longitude2=checkpoint.longitude,
                            latitude2=checkpoint.latitude,
                        )
                        if d < checkpoint.radius:
                            checkpoint.reached = True
                            print(f"{player.team} reached {checkpoint}")
                dist_to_finish = ut.distance_on_surface(
                    longitude1=player.longitude,
                    latitude1=player.latitude,
                    longitude2=config.start.longitude,
                    latitude2=config.start.latitude,
                )
                if dist_to_finish < config.start.radius and all(
                    ch.reached for ch in player.checkpoints
                ):
                    player.arrived = True
                    player.bonus = config.score_step - t
                    time_str = str(datetime.timedelta(seconds=int(t)))[2:]
                    print(f"{player.team} finished in {time_str}")
                    self.players_not_arrived.remove(player.team)
                    player.trip_time = t

            x, y, z = ut.to_xyz(
                ut.lon_to_phi(player.longitude), ut.lat_to_theta(player.latitude)
            )
            self.player_tracks[i, self.position_counter, ...] = [x, y, z]

        self.position_counter += 1

        inds = np.round(
            np.linspace(0, self.position_counter - 1, config.max_track_length)
        ).astype(int)
        self.buffers["player_positions"][
            self.bot_index_begin : self.bot_index_end, ...
        ] = self.player_tracks[:, inds, :][:, ::-1, :]

    def shutdown(self):
        print("inside engine shutdown")
        self.update_scoreboard()
        write_times({team: p.trip_time for team, p in self.players.items()})
        self.buffers["all_shutdown"][self.pid] = True

    def update(self):
        if self.buffers["game_flow"][0]:
            return

        # if len(self.players_not_arrived) == 0:
        #     return

        clock_time = time.time()
        t = clock_time - self.start_time
        dt = clock_time - self.previous_clock_time

        if dt > self.update_interval:
            dt = dt * config.seconds_to_hours
            self.weather.update_wind_tracers(t=np.array([t]), dt=dt)

            if len(self.players_not_arrived) > 0:
                if (clock_time - self.last_time_update) > config.time_update_interval:
                    self.update_scoreboard()
                    self.last_time_update = clock_time

                if (
                    clock_time - self.last_forecast_update
                ) > config.weather_update_interval:
                    self.forecast = self.weather.get_forecast(t)
                    self.last_forecast_update = clock_time

                self.call_player_bots(t=t * config.seconds_to_hours, dt=dt)
                self.move_players(self.weather, t=t, dt=dt)
                # self.weather.update_wind_tracers(t=np.array([t]), dt=dt)

                if len(self.players_not_arrived) == 0:
                    self.buffers["all_arrived"][self.pid] = True
                    self.update_scoreboard()

            self.previous_clock_time = clock_time

    def update_scoreboard(self):
        for i, player in enumerate(self.players.values()):
            self.buffers["player_status"][self.bot_index_begin + i, ...] = np.array(
                [
                    get_player_points(player),
                    player.distance_travelled,
                    player.speed,
                    len([ch for ch in player.checkpoints if ch.reached]),
                ],
                dtype=float,
            )

    def run(self, start_time: float):
        self.initialize_time(start_time)
        while not self.buffers["game_flow"][1]:
            self.update()
        self.shutdown()
