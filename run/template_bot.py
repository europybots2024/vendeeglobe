# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401

import numpy as np

from vendeeglobe import (
    Checkpoint,
    Heading,
    Instructions,
    Location,
    MapProxy,
    Vector,
    WeatherForecast,
    config,
)
from vendeeglobe.utils import distance_on_surface

# This is your team name
CREATOR = "TeamName"


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = CREATOR  # Mandatory attribute
        self.avatar = 1  # Optional attribute
        self.course = [
            Checkpoint(longitude=-45.5481686, latitude=39.0722068, radius=200),
            Checkpoint(longitude=-68.004373, latitude=18.180470, radius=10),
            Checkpoint(longitude=-80.0, latitude=9.4875, radius=10),
            Checkpoint(longitude=-79.3977636, latitude=8.6923598, radius=10),
            Checkpoint(longitude=-79.6065038, latitude=5.6673413, radius=10),
            Checkpoint(longitude=-168.943864, latitude=2.806318, radius=500),
            Checkpoint(longitude=174.900294, latitude=-17.801420, radius=10),
            Checkpoint(longitude=146.737149, latitude=-45.321510, radius=10),
            Checkpoint(longitude=114.565909, latitude=-36.310652, radius=10),
            Checkpoint(longitude=77.674694, latitude=-15.668984, radius=10),
            Checkpoint(longitude=51.301983, latitude=13.007233, radius=10),
            Checkpoint(longitude=43.853064, latitude=12.001511, radius=5),
            Checkpoint(longitude=34.008390, latitude=27.560352, radius=5),
            Checkpoint(longitude=33.028115, latitude=28.649649, radius=5),
            Checkpoint(longitude=32.542485, latitude=29.813090, radius=5),
            Checkpoint(longitude=32.251133, latitude=31.784320, radius=5),
            Checkpoint(latitude=34.557106, longitude=13.336454, radius=5),
            Checkpoint(latitude=38.427478, longitude=10.717964, radius=5),
            Checkpoint(latitude=36.318234, longitude=-1.976254, radius=5),
            Checkpoint(latitude=35.501014, longitude=-11.226080, radius=5),
            Checkpoint(latitude=43.830773, longitude=-10.694328, radius=5),
            Checkpoint(
                latitude=config.start.latitude,
                longitude=config.start.longitude,
                radius=5,
            ),
        ]
        # for ch in self.course[:9]:
        #     ch.reached = True
        for ch in self.course:
            ch.latitude += np.random.uniform(-0.1, 0.1)
            ch.longitude += np.random.uniform(-0.1, 0.1)

    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: WeatherForecast,
        map: MapProxy,
    ):
        """
        This is the method that will be called at every time step to get the
        instructions for the ship.

        Parameters
        ----------
        t:
            The current time in hours.
        dt:
            The time step in hours.
        longitude:
            The current longitude of the ship.
        latitude:
            The current latitude of the ship.
        heading:
            The current heading of the ship.
        speed:
            The current speed of the ship.
        vector:
            The current heading of the ship, expressed as a vector.
        forecast:
            The weather forecast for the next 5 days.
        map:
            The map of the world: 1 for sea, 0 for land.
        """
        instructions = Instructions()
        for ch in self.course:
            dist = distance_on_surface(
                longitude1=longitude,
                latitude1=latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            jump = dt * np.linalg.norm(speed)
            if dist < 2.0 * ch.radius + jump:
                instructions.sail = min(ch.radius / jump, 1)
            else:
                instructions.sail = 1.0
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions.location = Location(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions


class Bot2:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = CREATOR  # Mandatory attribute
        self.avatar = 2  # Optional attribute
        self.course = [
            Checkpoint(latitude=43.797109, longitude=-11.264905, radius=50),
            Checkpoint(longitude=-29.908577, latitude=17.999811, radius=50),
            Checkpoint(latitude=-11.441808, longitude=-29.660252, radius=50),
            Checkpoint(longitude=-63.240264, latitude=-61.025125, radius=50),
            Checkpoint(latitude=2.806318, longitude=-168.943864, radius=1990.0),
            Checkpoint(latitude=-62.052286, longitude=169.214572, radius=50.0),
            # Checkpoint(latitude=-57.746306, longitude=142.279800, radius=10.0),
            Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1190.0),
            Checkpoint(latitude=-39.438937, longitude=19.836265, radius=50.0),
            Checkpoint(latitude=14.881699, longitude=-21.024326, radius=50.0),
            Checkpoint(latitude=44.076538, longitude=-18.292936, radius=50.0),
            Checkpoint(
                latitude=config.start.latitude,
                longitude=config.start.longitude,
                radius=5,
            ),
        ]

        for ch in self.course:
            ch.latitude += np.random.uniform(-0.5, 0.5)
            ch.longitude += np.random.uniform(-0.5, 0.5)

    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: WeatherForecast,
        map: MapProxy,
    ):
        loc = None
        for ch in self.course:
            dist = distance_on_surface(
                longitude1=longitude,
                latitude1=latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                loc = Location(longitude=ch.longitude, latitude=ch.latitude)
                break

        return Instructions(location=loc)
