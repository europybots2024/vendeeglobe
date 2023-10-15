# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Tuple

from PIL import Image

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
    score_counter: int = 0
    player_update_interval: float = 1.0
    graphics_update_interval: float = 0.1
    time_update_interval: float = 1.0
    forecast_length: int = 5  # in days
    weather_update_interval: float = 3.0  # 3s = 12 hours
    seconds_to_hours = 4.0

    def pop_score(self) -> int:
        return (
            self.scores[self.score_counter]
            if self.score_counter < len(self.scores)
            else 0
        )


config = Config()


# class ImageLibrary:
#     def __init__(self):
#         self.images = {}
#         # files =
#         # print(files)
#         for f in glob(str(config.resourcedir / "ship*.png")):
#             img = Image.open(f)
#             img = img.convert("RGBA")
#             data = img.getdata()
#             new_data = np.array(data).reshape(img.height, img.width, 4)
#             for i in range(3):
#                 new_data[..., i] = int(round(rgb[i] * 255))
#             return Image.fromarray(new_data.astype(np.uint8))

#     # def get(self, fname: str):
#     #     if fname not in self.images:
#     #         self.images[fname] = mpl.image.imread(
#     #             str(config.resourcedir / fname), format="jpg"
#     #         )
#     #     return self.images[fname]


# image_library = ImageLibrary()


# Timing:

# 8 mins = 80 days
# 1 min  = 10 days
# 6 sec  =  1 day
# 1 sec  =  4 hours
# 0.25 s =  1 hour
