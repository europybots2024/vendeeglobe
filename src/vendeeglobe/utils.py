# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config


import hashlib


def string_to_color(input_string: str) -> str:
    hash_object = hashlib.md5(input_string.encode())
    hex_hash = hash_object.hexdigest()
    return "#" + hex_hash[:6]


def to_xyz(phi, theta, gl=False):
    # theta = np.radians(-theta)
    # phi = np.radians(phi)
    if gl:
        theta = np.pi - theta
    r = config.map_radius
    xpos = r * np.sin(theta) * np.cos(phi)
    ypos = r * np.sin(theta) * np.sin(phi)
    zpos = r * np.cos(theta)
    # return xpos, zpos, -ypos
    return xpos, ypos, zpos


def lat_to_theta(lat):
    return np.radians(90 - lat)


def lon_to_phi(lon):
    return np.radians((lon % 360) + 180)


def wrap(lat, lon):
    inds = (lat > 90) | (lat < -90)
    out_lat = np.maximum(np.minimum(lat, 180 - lat), -180 - lat)
    out_lon = lon.copy()
    out_lon[inds] += 180
    out_lon = ((out_lon + 180) % 360) - 180
    return out_lat, out_lon


# def vector_from_heading(h) -> np.ndarray:
#     h = h * np.pi / 180.0
#     return np.array([np.cos(h), np.sin(h)])


def wind_force(ship_vector, wind):
    # ship_vec = vector_from_heading(ship_heading)
    norm = np.linalg.norm(wind)
    vsum = ship_vector + wind / norm
    vsum /= np.linalg.norm(vsum)
    mag = np.abs(np.dot(ship_vector, vsum))
    return mag * norm * ship_vector
    # return mag * norm * vsum


def lon_degs_from_length(length, lat):
    """
    Given a length, compute how many degrees of longitude it represents at a given latitude.
    """
    return length / ((np.pi * config.map_radius * np.cos(np.radians(lat))) / 180)


def lat_degs_from_length(length):
    """
    Given a length, compute how many degrees of latitude it represents.
    """
    return length / (2.0 * np.pi * config.map_radius) * 360


def distance_on_surface(origin, to) -> float:
    """ """

    lon1 = np.radians(origin[0])
    lat1 = np.radians(origin[1])
    lon2 = np.radians(to[0])
    lat2 = np.radians(to[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # Use the Haversine formula to calculate the distance:

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return config.map_radius * c
