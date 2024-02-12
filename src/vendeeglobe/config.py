# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from .core import Checkpoint


@dataclass(frozen=True)
class Config:
    map_file: str = "world.jpg"
    map_radius: float = 6371.0
    resourcedir: Path = Path(__file__).parent / "resources"
    ntracers: int = 5000
    tracer_lifetime: int = 50
    start: Checkpoint = Checkpoint(longitude=-1.81, latitude=46.494275, radius=5.0)
    checkpoints: Tuple[Checkpoint, Checkpoint] = (
        Checkpoint(latitude=2.806318, longitude=-168.943864, radius=2000.0),
        Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1200.0),
    )
    graphics_update_interval: float = 0.1
    time_update_interval: float = 1.0
    forecast_length: int = 5  # in days
    weather_update_interval: float = 3.0  # 3s = 12 hours
    seconds_to_hours = 4.0
    avatar_size = [64, 64]
    score_step = 100_000
    max_name_length = 15
    max_track_length = 1000
    fps = 30
    time_limit: float = 8 * 60  # in seconds


config = Config()


# Timing:

# 8 mins = 80 days
# 1 min  = 10 days
# 6 sec  =  1 day
# 1 sec  =  4 hours
# 0.25 s =  1 hour
