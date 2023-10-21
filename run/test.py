# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from template_bot import Bot, Bot2

import vendeeglobe as vg

bots = [Bot(team="Alice")]

other_bots = []
for name in [
    "Bob",
    "Charlie",
    "Dave",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Oscar",
    "Peggy",
    "Sybil",
    "Trent",
    "Victor",
    "Walter",
]:
    other_bots.append(Bot2(team=name))
    for ch in other_bots[-1].course[:-1]:
        ch.longitude += np.random.uniform(-1, 1)
        ch.latitude += np.random.uniform(-1, 1)


start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)


vg.play(bots=bots + other_bots, start=start)
