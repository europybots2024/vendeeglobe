# SPDX-License-Identifier: BSD-3-Clause


from pathlib import Path

from .core import Checkpoint


class Config:
    def __init__(self):
        self.map_file = "world.jpg"
        self.map_radius = 6371
        self.resourcedir = Path(__file__).parent / "resources"
        self.ntracers = 5000
        self.tracer_lifetime = 50
        self.bot_polling_interval = 1.0
        self.start = Checkpoint(longitude=-4.773949, latitude=48.333422, radius=5.0)
        self.checkpoints = [
            Checkpoint(latitude=2.806318, longitude=-168.943864, radius=2000.0),
            Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1200.0),
        ]
        self.scores = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        self.player_update_interval = 1.0
        self.graphics_update_interval = 0.1
        self.time_update_interval = 1.0
        self.forecast_length = 5.0  # in days
