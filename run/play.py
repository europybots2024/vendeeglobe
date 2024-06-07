# SPDX-License-Identifier: BSD-3-Clause
import vendeeglobe as vg
from template_bot import Bot2

nbots = 200

# ais = np.random.choice([Bot, Bot2], nbots)
ais = [Bot2] * nbots

# players = {
#     "Alice": Bot,
#     "Bob": Bot2,
#     "Charlie": Bot,
#     "David": Bot2,
#     "Eve": Bot,
#     "Frank": Bot2,
# }


start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)

bots = []
for i, ai in enumerate(ais):
    bots.append(ai())
    bots[-1].team = f"Team-{i}"

# start = bots[-1].course[-3]

vg.play(bots=bots, start=start, seed=None, ncores=10, high_contrast=False)
