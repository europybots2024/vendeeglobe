# SPDX-License-Identifier: BSD-3-Clause

from template_bot import Bot, Bot2

import vendeeglobe as vg

bots = [Bot(team="Alice"), Bot2(team="Bob")]

start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)


vg.play(bots=bots, start=start, test=False)
