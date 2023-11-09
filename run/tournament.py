# SPDX-License-Identifier: BSD-3-Clause

import importlib
import glob

import vendeeglobe as vg


bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

vg.play(bots=bots, test=False)
