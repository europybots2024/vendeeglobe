# SPDX-License-Identifier: BSD-3-Clause

from .config import Config

config = Config()

from .engine import Engine
from .map import Checkpoint
from .player import Goto, Heading, Vector


def play(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    eng.run()
