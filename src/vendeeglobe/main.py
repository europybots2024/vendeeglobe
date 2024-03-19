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


class Clock:
    def __init__(self):
        self._start_time = None

    @property
    def start_time(self):
        if self._start_time is None:
            self._start_time = time.time()
        return self._start_time


clock = Clock()


def spawn_graphics(*args):
    graphics = Graphics(*args)
    graphics.run(start_time=clock.start_time)


def spawn_engine(*args):
    engine = Engine(*args)
    engine.run(start_time=clock.start_time)


def play(bots, seed=None, start=None, safe=False, ncores=8, high_contrast=False):

    pre_compile()

    n_sub_processes = ncores
    bots = {bot.team: bot for bot in bots}
    players = {name: Player(team=name, start=start) for name in bots}

    # TODO: Cheat!
    for player in players.values():
        for ch in player.checkpoints:
            ch.reached = True

    groups = np.array_split(list(bots.keys()), n_sub_processes)
    ntracers = (
        config.ntracers
        // (n_sub_processes * config.number_of_new_tracers)
        * config.number_of_new_tracers
    )
    tracer_positions = np.empty((n_sub_processes, config.tracer_lifetime, ntracers, 3))
    player_positions = np.empty((len(bots), config.max_track_length, 3))
    player_status = np.zeros((len(bots), 4))  # points, dist travelled, speed, checks
    game_flow = np.zeros(2, dtype=bool)  # pause, exit_from_graphics
    arrived = np.zeros(n_sub_processes, dtype=bool)
    shutdown = np.zeros(n_sub_processes, dtype=bool)

    weather = WeatherData(seed=seed)
    # map_terrain = np.load(os.path.join(config.resourcedir, 'mapdata.npz'))['sea_array']
    world_map = MapData()

    buffer_mapping = {
        'tracer_positions': tracer_positions,
        'player_positions': player_positions,
        'weather_u': weather.u,
        'weather_v': weather.v,
        'forecast_u': weather.forecast_u,
        'forecast_v': weather.forecast_v,
        'forecast_t': weather.forecast_times,
        'game_flow': game_flow,
        'player_status': player_status,
        'all_arrived': arrived,
        'all_shutdown': shutdown,
    }

    with SharedMemoryManager() as smm:

        buffers = {}
        for key, arr in buffer_mapping.items():
            mem = smm.SharedMemory(size=arr.nbytes)
            arr_shared = array_from_shared_mem(mem, arr.dtype, arr.shape)
            arr_shared[...] = arr
            buffers[key] = (mem, arr.dtype, arr.shape)

        graphics = Process(
            target=spawn_graphics,
            args=(
                players,
                high_contrast,
                {
                    key: buffers[key]
                    for key in (
                        'tracer_positions',
                        'player_positions',
                        'game_flow',
                        'player_status',
                        'all_arrived',
                        'all_shutdown',
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
                        safe,
                        world_map,
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
