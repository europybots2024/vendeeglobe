# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import vendeeglobe as vg

from template_bot import Bot, Bot2

bots = [Bot(team="Alice"), Bot2(team="Bob")]

start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)

# for i, p in enumerate(players.values()):
#     if i > 0:
#         for loc in p.course:
#             loc.latitude += np.random.uniform(-1.0, 1.0)
#             loc.longitude += np.random.uniform(-1.0, 1.0)

# start = vg.Location(latitude=47, longitude=-10)
# start = vg.Location(longitude=32.251133, latitude=31.784320)

vg.play(bots=bots, start=start, test=False)
