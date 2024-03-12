# SPDX-License-Identifier: BSD-3-Clause

import datetime
import os
import time
from multiprocessing import Lock, Process
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import SharedMemory
from typing import List, Optional, Tuple


import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


from . import config
from .core import Location
from .engine import Engine
from .graphics import Graphics
from .map import MapData, MapProxy, MapTextures
from .player import Player
from .utils import (
    array_from_shared_mem,
    distance_on_surface,
    longitude_difference,
    pre_compile,
    string_to_color,
)
from .weather import Weather, WeatherData


def spawn_graphics(*args):
    graphics = Graphics(*args)
    graphics.run()


def spawn_engine(*args):
    engine = Engine(*args)
    engine.run()


def play(bots, seed=None, time_limit=8 * 60, start=None, safe=False):
    n_sub_processes = 8
    # n = config.ntracers // self.n_sub_processes
    # self.ntracers_per_sub_process = [n for _ in range(self.n_sub_processes)]
    # for i in range(config.ntracers - sum(self.ntracers_per_sub_process)):
    #     self.ntracers_per_sub_process[i] += 1

    # bots = {}
    # players = {}
    # for bot in bots:
    #     team = bot.team
    #     bots[team] = bot
    #     players[team] = Player(team=team, avatar=getattr(bot, "avatar", 1), start=start)
    bots = {bot.team: bot for bot in bots}
    players = {name: Player(team=name, start=start) for name in bots}
    # # for name, bot in bots.items():
    # #     players[name] = Player(team=name, avatar=getattr(bot, 'avatar', 1), start=start)

    # Cheat!
    for player in players.values():
        for ch in player.checkpoints:
            ch.reached = True

    groups = np.array_split(list(bots.keys()), n_sub_processes)
    print('groups', groups)
    # bot_groups = []
    # for group in groups:
    #     bot_groups.append({name: bots[name] for name in group})
    # print(len(bot_groups))
    # print('keys', [it.keys() for it in bot_groups])

    ntracers = config.ntracers // n_sub_processes
    tracer_positions = np.empty((n_sub_processes, config.tracer_lifetime, ntracers, 3))
    player_positions = np.empty((len(bots), config.max_track_length, 3))
    player_delta_angles = np.empty((len(bots), 2))
    player_status = np.zeros((len(bots), 4))  # points, dist travelled, speed, checks

    weather = WeatherData(seed=seed, time_limit=time_limit)

    # map_terrain = MapData()

    map_terrain = np.load(os.path.join(config.resourcedir, 'mapdata.npz'))['sea_array']
    # # self.array = mapdata['array']
    # self.sea_array = mapdata

    game_flow = np.zeros(3, dtype=int)  # pause, exit, final

    # pre_compile()

    # self.time_limit = time_limit
    # self.start_time = None
    # self.safe = not test
    # self.test = test

    buffer_mapping = {
        'tracer_positions': tracer_positions,
        'player_positions': player_positions,
        'player_delta_angles': player_delta_angles,
        'weather_u': weather.u,
        'weather_v': weather.v,
        'forecast_u': weather.forecast_u,
        'forecast_v': weather.forecast_v,
        'game_flow': game_flow,
        'player_status': player_status,
    }

    with SharedMemoryManager() as smm:

        buffers = {}
        for key, arr in buffer_mapping.items():
            mem = smm.SharedMemory(size=arr.nbytes)
            arr_shared = array_from_shared_mem(mem, arr.dtype, arr.shape)
            arr_shared[...] = arr
            buffers[key] = (mem, arr.dtype, arr.shape)

        # tracer_positions_mem = smm.SharedMemory(size=tracer_positions.nbytes)
        # weather_u_mem = smm.SharedMemory(size=weather.u.nbytes)
        # weather_v_mem = smm.SharedMemory(size=weather.v.nbytes)
        # forecast_u_mem = smm.SharedMemory(size=weather.forecast_u.nbytes)
        # forecast_v_mem = smm.SharedMemory(size=weather.forecast_v.nbytes)
        # # default_texture_shared_mem = smm.SharedMemory(size=game_map.array.nbytes)
        # terrain_mem = smm.SharedMemory(size=map_terrain.nbytes)

        # player_positions_mem = smm.SharedMemory(size=player_positions.nbytes)
        # game_flow_mem = smm.SharedMemory(size=game_flow.nbytes)

        # # high_contrast_texture_shared_mem = smm.SharedMemory(
        # #     size=game_map.high_contrast_texture.nbytes
        # # )

        # # Populate buffers
        # for arr_mem in (
        #     (map_terrain, terrain_mem),
        #     (weather.u, weather_u_mem),
        #     (weather.v, weather_v_mem),
        #     (weather.forecast_u, forecast_u_mem),
        #     (weather.forecast_v, forecast_v_mem),
        #     (game_flow, game_flow_mem),
        # ):
        #     arr, mem = arr_mem
        #     arr_shared = array_from_shared_mem(mem, arr.dtype, arr.shape)
        #     arr_shared[...] = arr

        # # Expose buffers to sub-processes
        # buffers = {
        #     'tracer_positions': (
        #         tracer_positions_mem,
        #         tracer_positions.dtype,
        #         tracer_positions.shape,
        #     ),
        #     'player_positions': (
        #         player_positions_mem,
        #         player_positions.dtype,
        #         player_positions.shape,
        #     ),
        #     'weather_u': (weather_u_mem, weather.u.dtype, weather.u.shape),
        #     'weather_v': (weather_v_mem, weather.v.dtype, weather.v.shape),
        #     'forecast_u': (
        #         forecast_u_mem,
        #         weather.forecast_u.dtype,
        #         weather.forecast_u.shape,
        #     ),
        #     'forecast_v': (
        #         forecast_v_mem,
        #         weather.forecast_v.dtype,
        #         weather.forecast_v.shape,
        #     ),
        #     'game_flow': (game_flow_mem, game_flow.dtype, game_flow.shape),
        # }

        graphics = Process(
            target=spawn_graphics,
            args=(
                players,
                {
                    key: buffers[key]
                    for key in (
                        'tracer_positions',
                        'player_positions',
                        'player_delta_angles',
                        'game_flow',
                        'player_status',
                    )
                },
            ),
        )

        engines = []
        bot_index_begin = 0
        for i, group in enumerate(groups):
            engines.append(
                Process(
                    target=spawn_engine,
                    args=(
                        i,
                        seed,
                        {name: bots[name] for name in group},
                        {name: players[name] for name in group},
                        bot_index_begin,
                        buffers,
                        time_limit,
                        safe,
                    ),
                )
            )
            bot_index_begin += len(group)

        graphics.start()
        for engine in engines:
            engine.start()
        graphics.join()
        for engine in engines:
            engine.join()
