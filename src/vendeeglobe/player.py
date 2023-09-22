# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

import numpy as np

from . import config
from .utils import vector_from_heading, wrap


def wind_force(ship_heading, wind):
    ship_vec = vector_from_heading(ship_heading)
    norm = np.linalg.norm(wind)
    vsum = ship_vec + wind / norm
    vsum /= np.linalg.norm(vsum)
    mag = np.abs(np.dot(ship_vec, vsum))
    return mag * norm * vsum


class Player:
    def __init__(
        self,
        # ai: Any,
        team: str,
        # game_map: np.ndarray,
        score: int,
        number: int = 0,
        # base_locations: np.ndarray,
        # high_contrast: bool = False,
    ):
        # self.ai = ai
        # self.ai.team = team
        self.team = team
        self.score = score
        self.heading = 180.0 + 45.0 - (45 * number)
        self.speed = 0.0
        self.latitude = config.start['latitude']
        self.longitude = config.start['longitude']
        self.color = config.colors[number]

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)
            except:
                pass
        else:
            self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)

    def get_heading(self) -> float:
        return self.heading

    def move(self, t: float, dt: float, u, v):
        f = wind_force(self.get_heading(), np.array([u, v]))
        lat, lon = wrap(
            lat=np.array([self.latitude + f[1] * dt]),
            lon=np.array([self.longitude + f[0] * dt]),
        )
        self.latitude = lat[0]
        self.longitude = lon[0]
        return
