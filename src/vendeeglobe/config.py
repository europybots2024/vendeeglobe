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
    start: Checkpoint = Checkpoint(longitude=-4.773949, latitude=48.333422, radius=5.0)
    checkpoints: Tuple[Checkpoint, Checkpoint] = (
        Checkpoint(latitude=2.806318, longitude=-168.943864, radius=2000.0),
        Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1200.0),
    )
    scores: Tuple[int, ...] = (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)
    player_update_interval: float = 0.1  # 1.0
    graphics_update_interval: float = 0.1
    time_update_interval: float = 1.0
    forecast_length: int = 5  # in days
