# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

import numpy as np


@dataclass
class Location:
    longitude: float
    latitude: float


@dataclass
class Heading:
    angle: float


@dataclass
class Vector:
    u: float
    v: float


@dataclass
class Checkpoint:
    latitude: float
    longitude: float
    radius: float
    reached: bool = False


@dataclass
class WeatherForecast:
    u: np.ndarray
    v: np.ndarray
