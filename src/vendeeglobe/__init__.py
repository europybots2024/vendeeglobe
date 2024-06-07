# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401

from .config import config
from .core import Checkpoint, Heading, Instructions, Location, Vector
from .engine import Engine
from .main import play


# def play(*args, **kwargs):
#     eng = Engine(*args, **kwargs)
#     eng.run()
