# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    """
    A location on the globe. The latitude and longitude are in degrees.
    """

    longitude: float
    latitude: float


@dataclass
class Heading:
    """
    A heading angle for the ship: 0° is East, 90° is North, 180° is West, 270° is South.
    """

    angle: float


@dataclass
class Vector:
    """
    A vector to define the ship's heading.
    """

    u: float
    v: float


@dataclass
class Instructions:
    """
    Instructions for the ship.
    Define one of the following:
    - a location to go to
    - a heading to point to
    - a vector to follow

    Optionally, define a sail value between 0 and 1.
    """

    location: Optional[Location] = None
    heading: Optional[Heading] = None
    vector: Optional[Vector] = None
    sail: Optional[float] = None


@dataclass
class Checkpoint:
    """
    A checkpoint is a location on the globe with a radius.

    The latitude and longitude are in degrees.
    The radius is in kilometers.
    """

    latitude: float
    longitude: float
    radius: float
    reached: bool = False
