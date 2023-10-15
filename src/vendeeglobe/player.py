# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import asdict
from itertools import chain
from typing import Any, Optional, Sequence, Union, Tuple

import numpy as np

from . import config
from . import utils as utl
from .core import Checkpoint, Location, Heading, Vector


class Player:
    def __init__(
        self,
        # bot: Any,
        team: str,
        number: int = 0,
        start: Optional[Location] = None,
        avatar: Optional[Union[str, int]] = None,
    ):
        # self.bot = bot
        self.team = team
        self.score = None
        self.heading = 180.0
        self.speed = 0.0
        if start is None:
            self.latitude = config.start.latitude
            self.longitude = config.start.longitude
        else:
            self.latitude = start.latitude
            self.longitude = start.longitude
        self.color = utl.string_to_color(team)
        self.checkpoints = [
            Checkpoint(**asdict(checkpoint)) for checkpoint in config.checkpoints
        ]
        self.arrived = False
        self.distance_travelled = 0.0
        self.dlat = 0.0
        self.dlon = 0.0

    def execute_bot_instructions(self, instructions: Union[Location, Heading, Vector]):
        # instructions = None
        # if safe:
        #     try:
        #         instructions = self.bot.run(t=t, info=info)
        #     except:
        #         pass
        # else:
        #     instructions = self.bot.run(t=t, info=info)
        if isinstance(instructions, Location):
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
        """
        Point the vehicle towards the given longitude and latitude.
        """
        lon1 = np.radians(self.longitude)
        lat1 = np.radians(self.latitude)
        lon2 = np.radians(longitude)
        lat2 = np.radians(latitude)

        dlon = lon2 - lon1
        y = np.sin(dlon) * np.cos(lat2)
        x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        initial_bearing = -np.arctan2(y, x) + (np.pi * 0.5)
        self.set_heading((np.degrees(initial_bearing) + 360) % 360)

    def get_distance(self, longitude: float, latitude: float) -> float:
        """
        Compute the distance between the ship and the given longitude and latitude.
        """
        return utl.distance(self.get_position(), [longitude, latitude])

    def get_path(self, dt: float, u: float, v: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the path of the ship for the given time step.
        """
        pos = self.get_position()
        uv = np.array([u, v])
        self.speed = utl.wind_force(self.get_vector(), uv)
        f = self.speed * dt
        dist = np.array(
            [utl.lon_degs_from_length(f[0], pos[1]), utl.lat_degs_from_length(f[1])]
        )
        # print('distances', f, np.linalg.norm(f), np.linalg.norm(dist))

        # Race trace the path
        # norm = np.linalg.norm(uv)
        norm = np.linalg.norm(dist)
        ray = dist.reshape((2, 1)) * np.linspace(0, norm, max(20, int(norm) + 1))
        path = np.array(self.get_position()).reshape((2, 1)) + ray  # .astype(int)
        lat, lon = utl.wrap(lat=path[1, :], lon=path[0, :])
        return lat, lon
