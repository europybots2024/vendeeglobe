# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import asdict
from typing import Optional, Sequence, Tuple, Union

import numpy as np

from . import config
from . import utils as utl
from .core import Checkpoint, Heading, Location, Vector


class Player:
    def __init__(
        self,
        team: str,
        start: Optional[Location] = None,
    ):
        self.team = team
        self.bonus = 0
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
        self.sail = 1.0

    def execute_bot_instructions(self, instructions: Union[Location, Heading, Vector]):
        if [
            instructions.location,
            instructions.heading,
            instructions.vector,
            instructions.left,
            instructions.right,
        ].count(None) < 2:
            raise ValueError(
                "Instructions must define only one of location, heading, vector, "
                "left, or right."
            )
        if instructions.location is not None:
            self.goto(
                longitude=instructions.location.longitude,
                latitude=instructions.location.latitude,
            )
        elif instructions.heading is not None:
            self.set_heading(instructions.heading.angle)
        elif instructions.vector is not None:
            self.set_vector([instructions.vector.u, instructions.vector.v])
        elif instructions.left is not None:
            self.set_heading(self.heading + instructions.left)
        elif instructions.right is not None:
            self.set_heading(self.heading - instructions.right)
        if instructions.sail is not None:
            self.sail = min(max(0, instructions.sail), 1)

    def get_position(self) -> np.ndarray:
        return np.array([self.longitude, self.latitude])

    def get_heading(self) -> float:
        return self.heading

    def set_heading(self, angle: float):
        """
        Set the heading angle (in degrees) of the vehicle.
        East is 0, North is 90, West is 180, South is 270.
        """
        self.heading = angle % 360

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
        self.set_heading(
            utl.goto(
                origin=Location(longitude=self.longitude, latitude=self.latitude),
                to=Location(longitude=longitude, latitude=latitude),
            )
        )

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
        vec = utl.wind_force(self.get_vector(), uv)
        self.speed = np.linalg.norm(vec)
        f = vec * dt * self.sail
        dist = np.array(
            [utl.lon_degs_from_length(f[0], pos[1]), utl.lat_degs_from_length(f[1])]
        )
        # Race trace the path
        norm = np.linalg.norm(dist)
        ray = dist.reshape((2, 1)) * np.linspace(0, 1, (int(norm) + 1) * 8)
        path = np.array(self.get_position()).reshape((2, 1)) + ray
        lat, lon = utl.wrap(lat=path[1, :], lon=path[0, :])
        return lat, lon
