# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

import numpy as np

from . import config
from .utils import wrap


def wind_force(ship_vector, wind):
    # ship_vec = vector_from_heading(ship_heading)
    norm = np.linalg.norm(wind)
    vsum = ship_vector + wind / norm
    vsum /= np.linalg.norm(vsum)
    mag = np.abs(np.dot(ship_vector, vsum))
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

    def get_position(self) -> np.ndarray:
        return np.array([self.longitude, self.latitude])

    def get_heading(self) -> float:
        return self.heading

    def get_vector(self) -> np.ndarray:
        h = self.get_heading() * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    # def ray_trace(self, f: np.ndarray, dt: float) -> np.ndarray:
    #     # vt = self.speed * dt
    #     ray = f.reshape((2, 1)) * np.linspace(0, f, int(f) + 1)
    #     return (np.array(self.avatar.position()).reshape((2, 1)) + ray).astype(int)

    def get_path(self, t: float, dt: float, u, v, n):
        f = wind_force(self.get_vector(), np.array([u, v])) * n * dt

        # Race trace the path
        ray = f.reshape((2, 1)) * np.linspace(0, n, max(20, int(n) + 1))
        path = np.array(self.get_position()).reshape((2, 1)) + ray  # .astype(int)
        # print(self.team)
        # print(f, f.shape)
        # print(ray, ray.shape)
        # print(path, path.shape)
        lat, lon = wrap(lat=path[1, :], lon=path[0, :])
        return lat, lon

        lat, lon = wrap(
            lat=np.array([self.latitude + f[1]]),
            lon=np.array([self.longitude + f[0]]),
        )
        self.latitude = lat[0]
        self.longitude = lon[0]
        return
