# SPDX-License-Identifier: BSD-3-Clause

import importlib
import glob

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
    speedup=None,  # Time speedup factor
    course_preview=None,  # A list of checkpoints should be supplied
)
