# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from vendeeglobe import Checkpoint

# This is your team name
CREATOR = "TeamName"


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self, team=CREATOR):
        self.team = team  # Mandatory attribute
        self.course = [
            Checkpoint(
                longitude=-45.5481686, latitude=39.0722068, radius=10, reached=False
            ),
            Checkpoint(longitude=-68.004373, latitude=18.180470, radius=0.5),
            Checkpoint(longitude=-80.3, latitude=9.4875, radius=0.5),
            Checkpoint(longitude=-79.3977636, latitude=8.6923598, radius=0.5),
            Checkpoint(longitude=-79.6065038, latitude=5.6673413, radius=0.5),
            Checkpoint(longitude=-161.3416118, latitude=10.6814994, radius=0.5),
        ]

    def run(self, t: float, dt: float, info: dict):
        instructions = {}
        for ch in self.course:
            dist = np.sqrt(
                (info['longitude'] - ch.longitude) ** 2
                + (info['latitude'] - ch.latitude) ** 2
            )
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions['goto'] = dict(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions
