# SPDX-License-Identifier: BSD-3-Clause

import vendeeglobe as vg

from template_bot import Bot

names = [
    'Neil',
    # 'Alex',
    # 'Kevin',
]

players = {name: Bot(team=name) for name in names}
start = {'longitude': -68.004373, 'latitude': 18.180470}
start = None
vg.play(players=players, start=start)
