# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import vendeeglobe as vg

from template_bot import Bot, Bot2

bots = [Bot(team="Alice"), Bot2(team="Bob")]

start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)


vg.play(bots=bots, start=start, test=False)
