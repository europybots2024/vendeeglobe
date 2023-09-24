# SPDX-License-Identifier: BSD-3-Clause

import vendeeglobe as vg

from template_bot import Bot

names = [
    'Neil',
    # 'Alex',
    # 'Kevin',
]

players = {name: Bot(team=name) for name in names}

vg.play(players=players, width=900, height=600)
