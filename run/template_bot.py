# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from vendeeglobe import Checkpoint
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
        ]
        for ch in self.course[:-1]:
            ch.reached = True

    def run(self, t: float, dt: float, info: dict):
        instructions = {}
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
                instructions['goto'] = dict(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions
