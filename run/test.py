import vendeeglobe as vg

names = [
    'Afonso',
    'Drew',
    'Greg',
    'Jankas',
    'Mads',
    'Simon',
    'Sun',
]

players = {name: None for name in names}

vg.play(players=players, width=900, height=600)
