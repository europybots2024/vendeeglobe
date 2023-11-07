# SPDX-License-Identifier: BSD-3-Clause

import vendeeglobe as vg
from template_bot import Bot, Bot2


players = {"Alice": Bot, "Bob": Bot2}


start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)

bots = []
for team, bot in players.items():
    bots.append(bot())
    bots[-1].team = team

vg.play(
    bots=bots,
    start=start,
    seed=None,
    time_limit=60 * 8,
    speedup=None,
    course_preview=bots[0].course,
)
