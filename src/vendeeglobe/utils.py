# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config


# def to_xyz(latitude, longitude):
#     theta = np.radians(lat_to_theta(latitude))
#     phi = np.radians(lon_to_phi(longitude))
#     xpos = config.map_radius * np.sin(theta) * np.cos(phi)
#     ypos = config.map_radius * np.sin(theta) * np.sin(phi)
#     zpos = config.map_radius * np.cos(theta)
#     return np.array([xpos, zpos, -ypos]).T


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
