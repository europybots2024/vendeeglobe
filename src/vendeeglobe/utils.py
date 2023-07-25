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


def to_xyz(phi, theta):
    # theta = np.radians(-theta)
    # phi = np.radians(phi)
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
    return np.radians(lon % 360)


def wrap_lat(x):
    return np.maximum(np.minimum(x, 180 - x), -180 - x)


def wrap_lon(x):
    return ((x + 180) % 360) - 180
