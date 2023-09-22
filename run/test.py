# SPDX-License-Identifier: BSD-3-Clause

import vendeeglobe as vg

names = [
    'Neil',
    'Alex',
    'Kevin',
]

players = {name: None for name in names}

vg.play(players=players, width=900, height=600)
