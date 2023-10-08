# SPDX-License-Identifier: BSD-3-Clause

import uuid
from dataclasses import dataclass
from itertools import chain
from typing import Any, Iterator, Sequence, Union, Tuple

import numpy as np

from . import config
from .map import Checkpoint
from . import utils as utl


@dataclass
class Goto:
    longitude: float
    latitude: float


@dataclass
class Heading:
    angle: float


@dataclass
class Vector:
    u: float
    v: float


class Player:
    def __init__(
        self,
        # ai: Any,
        bot: Any,
        team: str,
        # game_map: np.ndarray,
        # score: int,
        number: int = 0,
        # base_locations: np.ndarray,
        # high_contrast: bool = False,
        start: dict = None,
    ):
        # self.ai = ai
        self.bot = bot
        # self.ai.team = team
        self.team = team
        self.score = None
        self.heading = 180.0 + 45.0 - (45 * number)
        self.speed = 0.0
        if start is None:
            self.latitude = config.start['latitude']
            self.longitude = config.start['longitude']
        else:
            self.latitude = start['latitude']
            self.longitude = start['longitude']
        self.color = utl.string_to_color(team)
        self.checkpoints = [
            Checkpoint(**checkpoint) for checkpoint in config.checkpoints
        ]
        self.arrived = False

    def execute_bot(self, t: float, info: dict, safe: bool = False):
        instructions = None
        if safe:
            try:
                instructions = self.bot.run(t=t, info=info)
            except:
                pass
        else:
            instructions = self.bot.run(t=t, info=info)
        if isinstance(instructions, Goto):
            self.goto(longitude=instructions.longitude, latitude=instructions.latitude)
        elif isinstance(instructions, Heading):
            self.set_heading(instructions.angle)
        elif isinstance(instructions, Vector):
            self.set_vector([instructions.u, instructions.v])

    def get_position(self) -> np.ndarray:
        return np.array([self.longitude, self.latitude])

    def get_heading(self) -> float:
        return self.heading

    def set_heading(self, angle: float):
        """
        Set the heading angle (in degrees) of the vehicle.
        East is 0, North is 90, West is 180, South is 270.
        """
        self.heading = angle

    def get_vector(self) -> np.ndarray:
        h = self.get_heading() * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def set_vector(self, vec: Union[np.ndarray, Sequence[float]]):
        """
        Set the vehicle's heading according to the given vector [vx, vy].
        """
        vec = np.asarray(vec) / np.linalg.norm(vec)
        h = np.arccos(np.dot(vec, [1, 0])) * 180 / np.pi
        if vec[1] < 0:
            h = 360 - h
        self.set_heading(h)

    def goto(self, longitude: float, latitude: float):
        """ """
        # self.set_vector([longitude - self.longitude, latitude - self.latitude])

        lon1 = np.radians(self.longitude)
        lat1 = np.radians(self.latitude)
        lon2 = np.radians(longitude)
        lat2 = np.radians(latitude)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        # Use the Haversine formula to calculate the distance:

        # a = sin²(dlat/2) + cos(lat1) * cos(lat2) * sin²(dlon/2)
        # c = 2 * atan2(√a, √(1-a))
        # distance = R * c
        # Where:

        # R is the radius of the Earth (approximately 6,371 kilometers or 3,959 miles).
        # Calculate the initial bearing (direction):
        y = np.sin(dlon) * np.cos(lat2)
        x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        initial_bearing = -np.arctan2(y, x) + (np.pi * 0.5)
        self.set_heading((np.degrees(initial_bearing) + 360) % 360)
        return
        # d, xl, yl = tls.periodic_distances(self.x, self.y, x, y)
        # ind = np.argmin(d)
        # self.set_vector(
        #     [xl[ind] - (self.x + config.nx), yl[ind] - (self.y + config.ny)]
        # )

    def get_distance(self, longitude: float, latitude: float) -> float:
        """ """
        return utl.distance(self.get_position(), [longitude, latitude])

    #     lon1 = np.radians(self.longitude)
    #     lat1 = np.radians(self.latitude)
    #     lon2 = np.radians(longitude)
    #     lat2 = np.radians(latitude)

    #     dlon = lon2 - lon1
    #     dlat = lat2 - lat1
    #     # Use the Haversine formula to calculate the distance:

    #     a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    #     c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    #     return config.map_radius * c
    #     # Where:

    # # def ray_trace(self, f: np.ndarray, dt: float) -> np.ndarray:
    # #     # vt = self.speed * dt
    # #     ray = f.reshape((2, 1)) * np.linspace(0, f, int(f) + 1)
    # #     return (np.array(self.avatar.position()).reshape((2, 1)) + ray).astype(int)

    def get_path(self, t: float, dt: float, u, v):
        pos = self.get_position()
        uv = np.array([u, v])
        f = utl.wind_force(self.get_vector(), uv) * dt
        dist = np.array(
            [utl.lon_degs_from_length(f[0], pos[1]), utl.lat_degs_from_length(f[1])]
        )

        # Race trace the path
        norm = np.linalg.norm(uv)
        ray = dist.reshape((2, 1)) * np.linspace(0, norm, max(20, int(norm) + 1))
        path = np.array(self.get_position()).reshape((2, 1)) + ray  # .astype(int)
        # print(self.team)
        # print(f, f.shape)
        # print(ray, ray.shape)
        # print(path, path.shape)
        lat, lon = utl.wrap(lat=path[1, :], lon=path[0, :])
        return lat, lon

        # lat, lon = wrap(
        #     lat=np.array([self.latitude + f[1]]),
        #     lon=np.array([self.longitude + f[0]]),
        # )
        # self.latitude = lat[0]
        # self.longitude = lon[0]
        # return
