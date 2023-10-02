# SPDX-License-Identifier: BSD-3-Clause

import vendeeglobe as vg

from template_bot import Bot

names = [
    'Neil',
    # 'Alex',
    # 'Kevin',
]

players = {name: Bot(team=name) for name in names}
start = None
# start = {'longitude': -68.004373, 'latitude': 18.180470}
# start = {'longitude': -79.6065038, 'latitude': 5.6673413}
# start = None
# start = dict(longitude=77.674694, latitude=-15.668984)
# start = {'latitude': 43.991131, 'longitude': -24.213527}
vg.play(players=players, start=start)
