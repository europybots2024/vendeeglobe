# SPDX-License-Identifier: BSD-3-Clause

import importlib
import glob

import os
# Enforces the use of wayland, even on Gnome systems. Which is needed by opengl.
os.environ["QT_QPA_PLATFORM"] = "wayland"

import vendeeglobe as vg


bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)

vg.play(
    bots=bots,  # List of bots to use
    start=start,  # Starting location for all bots
    seed=None,  # Seed for generating the weather
    time_limit=60 * 8,  # Time limit in seconds
    speedup=None,  # Time speedup factor (this one is a little buggy!)
    course_preview=None,  # A list of checkpoints should be supplied: eg bots[0].course
    high_contrast=False,
)
