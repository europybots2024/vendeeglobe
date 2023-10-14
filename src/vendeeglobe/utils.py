# SPDX-License-Identifier: BSD-3-Clause

from typing import Tuple, Union

import numpy as np

from . import config


import hashlib


def string_to_color(input_string: str) -> str:
    hash_object = hashlib.md5(input_string.encode())
    hex_hash = hash_object.hexdigest()
    return "#" + hex_hash[:6]


def to_xyz(
    phi: Union[float, np.ndarray], theta: Union[float, np.ndarray], gl: bool = False
) -> Tuple[
    Union[float, np.ndarray], Union[float, np.ndarray], Union[float, np.ndarray]
]:
    if gl:
        theta = np.pi - theta
    r = config.map_radius
    xpos = r * np.sin(theta) * np.cos(phi)
    ypos = r * np.sin(theta) * np.sin(phi)
    zpos = r * np.cos(theta)
    return xpos, ypos, zpos


def lat_to_theta(lat: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    return np.radians(90 - lat)


def lon_to_phi(lon: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    return np.radians((lon % 360) + 180)


def wrap(
    lat: Union[float, np.ndarray], lon: Union[float, np.ndarray]
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    inds = (lat > 90) | (lat < -90)
    out_lat = np.maximum(np.minimum(lat, 180 - lat), -180 - lat)
    out_lon = lon.copy()
    out_lon[inds] += 180
    out_lon = ((out_lon + 180) % 360) - 180
    return out_lat, out_lon


def wind_force(ship_vector: np.ndarray, wind: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(wind)
    vsum = ship_vector + wind / norm
    vsum /= np.linalg.norm(vsum)
    mag = np.abs(np.dot(ship_vector, vsum))
    return mag * norm * ship_vector


def lon_degs_from_length(length: np.ndarray, lat: np.ndarray) -> np.ndarray:
    """
    Given a length, compute how many degrees of longitude it represents at a given latitude.
    """
    return length / ((np.pi * config.map_radius * np.cos(np.radians(lat))) / 180)


def lat_degs_from_length(length: np.ndarray) -> np.ndarray:
    """
    Given a length, compute how many degrees of latitude it represents.
    """
    return length / (2.0 * np.pi * config.map_radius) * 360


def distance_on_surface(
    origin: Union[Tuple[float, float], np.ndarray],
    to: Union[Tuple[float, float], np.ndarray],
) -> float:
    """
    Use the Haversine formula to calculate the distance on the surface of the globe
    between two points given by their longitude and latitude.
    """
    lon1 = np.radians(origin[0])
    lat1 = np.radians(origin[1])
    lon2 = np.radians(to[0])
    lat2 = np.radians(to[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return config.map_radius * c


def longitude_difference(lon1, lon2):
    # Calculate the absolute difference in longitudes
    lon_diff = abs(lon1 - lon2)
    # Check if the crossing of the +/- 180 degrees line is shorter
    crossing_diff = 360 - lon_diff
    # Return the shorter of the two differences
    return min(lon_diff, crossing_diff)
