# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401

from .config import config
from .core import Checkpoint, Heading, Instructions, Location, Vector
from .engine import Engine


def play(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    eng.run()


__all__ = [
    "Checkpoint",
    "Heading",
    "Instructions",
    "Location",
    "Vector",
    "config",
    "play",
]
