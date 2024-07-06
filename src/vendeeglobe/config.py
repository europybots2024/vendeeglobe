# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from .core import Checkpoint


@dataclass(frozen=True)
class Config:
    map_file: str
    map_radius: float
    resourcedir: Path
    ntracers: int
    tracer_lifetime: int
    start: Checkpoint
    checkpoints: Tuple[Checkpoint, Checkpoint]
    graphics_update_interval: float
    time_update_interval: float
    forecast_length: int
    weather_update_interval: float
    seconds_to_hours: float
    score_step: float
    max_name_length: int


config = Config(
    map_file="world.jpg",
    map_radius=6371.0,
    resourcedir=Path(__file__).parent / "resources",
    ntracers=5000,
    tracer_lifetime=50,
    start=Checkpoint(longitude=-1.81, latitude=46.494275, radius=5.0),
    checkpoints=(
        Checkpoint(latitude=2.806318, longitude=-168.943864, radius=2000.0),
        Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1200.0),
    ),
    graphics_update_interval=0.1,
    time_update_interval=1.0,
    forecast_length=5,  # in days
    weather_update_interval=3.0,  # 3s = 12 hours
    seconds_to_hours=4.0,
    score_step=100_000,
    max_name_length=15,
)


# Timing:

# 8 mins = 80 days
# 1 min  = 10 days
# 6 sec  =  1 day
# 1 sec  =  4 hours
# 0.25 s =  1 hour
