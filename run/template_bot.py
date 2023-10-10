# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from vendeeglobe import Checkpoint, Location, Heading, Vector
from vendeeglobe.utils import distance_on_surface

# This is your team name
CREATOR = "TeamName"


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self, team=CREATOR):
        self.team = team  # Mandatory attribute
        self.course = [
            Checkpoint(longitude=-45.5481686, latitude=39.0722068, radius=200),
            Checkpoint(longitude=-68.004373, latitude=18.180470, radius=10),
            Checkpoint(longitude=-80.3, latitude=9.4875, radius=10),
            Checkpoint(longitude=-79.3977636, latitude=8.6923598, radius=10),
            Checkpoint(longitude=-79.6065038, latitude=5.6673413, radius=10),
            Checkpoint(longitude=-168.943864, latitude=2.806318, radius=500),
            Checkpoint(longitude=174.900294, latitude=-16.801420, radius=10),
            Checkpoint(longitude=146.737149, latitude=-45.321510, radius=10),
            Checkpoint(longitude=114.565909, latitude=-36.310652, radius=10),
            Checkpoint(longitude=77.674694, latitude=-15.668984, radius=10),
            Checkpoint(longitude=51.301983, latitude=13.007233, radius=10),
            Checkpoint(longitude=43.413064, latitude=12.601511, radius=5),
            Checkpoint(longitude=34.008390, latitude=27.560352, radius=5),
            Checkpoint(longitude=33.028115, latitude=28.649649, radius=5),
            Checkpoint(longitude=32.542485, latitude=29.813090, radius=5),
            Checkpoint(longitude=32.251133, latitude=31.784320, radius=5),
            Checkpoint(longitude=-4.773949, latitude=48.333422, radius=5.0),
        ]
        # for ch in self.course[:-1]:
        #     ch.reached = True

    def run(self, t: float, info: dict):
        instructions = None
        for ch in self.course:
            dist = distance_on_surface(
                origin=[info['longitude'], info['latitude']],
                to=[ch.longitude, ch.latitude],
            )
            # dist = np.sqrt(
            #     (info['longitude'] - ch.longitude) ** 2
            #     + (info['latitude'] - ch.latitude) ** 2
            # )
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions = Location(longitude=ch.longitude, latitude=ch.latitude)
                break

        return instructions
