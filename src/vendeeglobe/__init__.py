# SPDX-License-Identifier: BSD-3-Clause

from .config import Config

config = Config()

from .engine import Engine
from .core import Checkpoint, Location, Heading, Vector


def play(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    eng.run()
