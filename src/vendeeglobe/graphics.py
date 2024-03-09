# SPDX-License-Identifier: BSD-3-Clause
import datetime
import time
from typing import Any, Dict

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from matplotlib.colors import to_rgba
from OpenGL.GL import *  # noqa
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.Qt import QtCore


try:
    from PyQt5.QtWidgets import (
        QCheckBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QSizePolicy,
        QSlider,
        QVBoxLayout,
        QWidget,
    )
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (
        QMainWindow,
        QWidget,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QCheckBox,
        QSizePolicy,
        QSlider,
        QFrame,
    )
    from PySide2.QtCore import Qt


from . import config
from . import utils as ut
from .map import MapTextures
from .player import Player
from .scores import (
    finalize_scores,
    get_player_points,
    read_fastest_times,
    read_scores,
    write_fastest_times,
)
from .sphere import GLTexturedSphereItem
from .utils import array_from_shared_mem, string_to_color
from .weather import Weather


class Graphics:
    def __init__(
        self,
        #  game_map: Map,
        # total_number_of_tracers: int,
        # tracer_shared_mem: SharedMemory,
        # tracer_shared_data_dtype: np.dtype,
        # tracer_shared_data_shape: Tuple[int, ...],
        # player_colors: Dict[str, str],
        # player_names,
        players: Dict[str, Player],
        test: bool,
        buffers: Dict[str, Any],
        # tracer_positions: np.ndarray,
        # player_positions: np.ndarray,
        # default_texture: np.array,
    ):

        self.scoreboard_max_players = 20

        self.initialize_time()

        print("Composing graphics...", end=" ", flush=True)
        self.app = pg.mkQApp("Vendee Globe")
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle("Vendee Globe")
        self.window.setCameraPosition(
            distance=config.map_radius * 4,
            elevation=config.start.latitude,
            azimuth=180 + config.start.longitude,
        )

        self.map_textures = MapTextures()

        self.default_texture = np.fliplr(
            np.transpose(self.map_textures.default_texture, axes=[1, 0, 2])
        )
        self.high_contrast_texture = np.transpose(
            self.map_textures.contrast_texture, axes=[1, 0, 2]
        )

        self.players = players
        self.test = test

        self.buffers = {
            key: array_from_shared_mem(*value) for key, value in buffers.items()
        }

        # self.default_texture = np.zeros((64, 128, 4), dtype='uint8')
        # self.default_texture[..., 3] = 255
        # self.high_contrast_texture = self.default_texture.copy()

        self.sphere = GLTexturedSphereItem(self.default_texture)
        self.sphere.setGLOptions("opaque")
        self.window.addItem(self.sphere)

        nstars = 5000
        x, y, z = ut.to_xyz(
            np.random.uniform(0, 2.0 * np.pi, nstars),
            np.random.normal(0.5 * np.pi, 0.4, nstars),
        )
        f = 100
        self.background_stars = gl.GLScatterPlotItem(
            pos=f * np.array([x, y, z]).T,
            color=np.ones((nstars, 4)),
            size=1,
            pxMode=True,
        )
        self.background_stars.setGLOptions("opaque")
        self.window.addItem(self.background_stars)

        # Add checkpoints
        scl = [0.96, 0.99]
        for i, ch in enumerate(config.checkpoints):
            md = gl.MeshData.cylinder(
                rows=10,
                cols=20,
                radius=[ch.radius, ch.radius],
                length=scl[i] * config.map_radius,
            )
            color = (0.2, 0.2, 0.2, 1)
            colors = np.tile(color, md.faceCount()).reshape((-1, 4))
            md.setFaceColors(colors)
            mesh = gl.GLMeshItem(
                meshdata=md,
                smooth=True,
                drawEdges=True,
                edgeColor=color,
            )
            mesh.rotate(np.degrees(ut.lat_to_theta(ch.latitude)), 0, 1, 0)
            mesh.rotate(np.degrees(ut.lon_to_phi(ch.longitude)), 0, 0, 1)
            self.window.addItem(mesh)

        # self.tracer_positions = array_from_shared_mem(
        #     tracer_shared_mem, tracer_shared_data_dtype, tracer_shared_data_shape
        # )
        self.tracer_positions = self.buffers['tracer_positions']

        # # Add tracers
        # x, y, z = ut.to_xyz(
        #     ut.lon_to_phi(weather.tracer_lon.ravel()),
        #     ut.lat_to_theta(weather.tracer_lat.ravel()),
        # )

        # size = (config.tracer_lifetime, total_number_of_tracers)
        self.default_tracer_colors = np.ones(self.tracer_positions.shape[:-1] + (4,))
        self.default_tracer_colors[..., 3] = np.linspace(
            1, 0, config.tracer_lifetime
        ).reshape((-1, 1))

        # self.default_tracer_colors = weather.tracer_colors
        self.high_contrast_tracer_colors = self.default_tracer_colors.copy()
        self.high_contrast_tracer_colors[..., :3] *= 0.8
        self.tracers = gl.GLScatterPlotItem(
            pos=self.tracer_positions.reshape((-1, 3)),
            color=self.default_tracer_colors.reshape((-1, 4)),
            size=2,
            pxMode=True,
        )
        # print(self.tracer_positions.reshape((-1, 3)).shape)
        # self.tracers.setGLOptions("opaque")
        self.tracers.setGLOptions('translucent')
        self.window.addItem(self.tracers)

        # # Add players
        # latitudes = np.array([player.latitude for player in players.values()])
        # longitudes = np.array([player.longitude for player in players.values()])
        self.player_positions = self.buffers['player_positions']
        player_colors = [string_to_color(p.team) for p in self.players.values()]
        colors = np.array([to_rgba(color) for color in player_colors])
        # x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))

        self.player_markers = gl.GLScatterPlotItem(
            pos=self.player_positions,
            color=colors,
            size=10,
            pxMode=True,
        )
        self.player_markers.setGLOptions("opaque")
        # # self.tracers.setGLOptions('translucent')
        self.window.addItem(self.player_markers)

        self.tracks = []
        self.avatars = []
        # self.labels = {}
        for i, player in enumerate(self.players.values()):
            # for i in range(len(self.player_positions)):
            x, y, z = ut.to_xyz(
                ut.lon_to_phi(player.longitude),
                ut.lat_to_theta(player.latitude),
            )
            pos = np.array([[x], [y], [z]]).T
            track = gl.GLLinePlotItem(
                # pos=self.player_positions[i, 0, :],
                pos=pos,
                color=tuple(colors[i]),
                width=4,
                antialias=True,
            )
            track.setGLOptions("opaque")
            self.window.addItem(track)
            self.tracks.append(track)

            # avatar = gl.GLImageItem(
            #     np.fliplr(np.transpose(np.array(player.avatar), axes=[1, 0, 2]))
            # )
            # offset = config.avatar_size[0] / 2
            # avatar.translate(-offset, -offset, 0)
            # avatar.rotate(90, 1, 0, 0)
            # avatar.rotate(180, 0, 0, 1)
            # avatar.translate(0, config.map_radius, 0)
            # avatar.rotate(90, 0, 0, 1)
            # avatar.rotate(player.longitude, 0, 0, 1)
            # perp_vec = np.cross([x, y, 0], [0, 0, 1])
            # perp_vec /= np.linalg.norm(perp_vec)
            # avatar.rotate(player.latitude, *perp_vec)
            # self.window.addItem(avatar)
            # self.avatars.append(avatar)

        self.fastest_times = read_fastest_times(self.players)
        print(f'done [{time.time() - self.start_time:.2f} s]')

    def initialize_time(self):
        self.start_time = time.time()
        self.last_player_update = self.start_time
        self.last_graphics_update = self.start_time
        self.last_time_update = self.start_time
        self.last_forecast_update = self.start_time
        self.previous_clock_time = self.start_time
        self.update_interval = 1 / config.fps

    def update_wind_tracers(self):  # , tracer_lat: np.ndarray, tracer_lon: np.ndarray):
        # x, y, z = ut.to_xyz(
        #     ut.lon_to_phi(tracer_lon.ravel()),
        #     ut.lat_to_theta(tracer_lat.ravel()),
        # )
        # print("Graphics", self.tracer_positions.min(), self.tracer_positions.max())

        # Lock the positions array
        # self.buffers['game_flow'][2] = 1
        self.tracers.setData(pos=self.tracer_positions.reshape((-1, 3)))
        # self.buffers['game_flow'][2] = 0

    def update_player_positions(self):
        #     latitudes = np.array([player.latitude for player in players.values()])
        #     longitudes = np.array([player.longitude for player in players.values()])
        #     x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))
        #     self.players.setData(pos=np.array([x, y, z]).T)
        self.player_markers.setData(pos=self.player_positions[:, 0, :])

        for i in range(len(self.player_positions)):
            self.tracks[i].setData(pos=self.player_positions[i, ...])
            # self.avatars[i].rotate(self.buffers['player_delta_angles'][i, 1], 0, 0, 1)
            # perp_vec = np.cross(self.player_positions[i, 0, :], [0, 0, 1])
            # perp_vec /= np.linalg.norm(perp_vec)
            # self.avatars[i].rotate(self.buffers['player_delta_angles'][i, 0], *perp_vec)

        # # for i, (name, player) in enumerate(players.items()):
        #     if not player.arrived:
        #         arr = np.array([x[i], y[i], z[i]])
        #         pos = np.vstack(
        #             [self.tracks[name]['pos'], arr],
        #         )
        #         npos = len(pos)
        #         step = (npos // 1000) if npos > 1000 else 1
        #         self.tracks[name]['artist'].setData(pos=pos[::step])
        #         self.tracks[name]['pos'] = pos
        #         self.avatars[name].rotate(player.dlon, 0, 0, 1)
        #         perp_vec = np.cross([x[i], y[i], 0], [0, 0, 1])
        #         perp_vec /= np.linalg.norm(perp_vec)
        #         self.avatars[name].rotate(player.dlat, *perp_vec)

    def toggle_wind_tracers(self, val):
        self.tracers.setVisible(val)

    def toggle_texture(self, val):
        if val:
            self.sphere.setData(self.high_contrast_texture)
            self.tracers.setData(color=self.high_contrast_tracer_colors)
        else:
            self.sphere.setData(self.default_texture)
            self.tracers.setData(color=self.default_tracer_colors)

    def set_tracer_thickness(self, val):
        self.tracers.setData(size=val)

    def toggle_stars(self, val):
        self.background_stars.setVisible(val)

    def update_scoreboard(self):
        status = [
            (
                self.buffers['player_status'][i, 0],  # points
                self.buffers['player_status'][i, 1],  # distance travelled
                player.team,
                self.buffers['player_status'][i, 2],  # speed
                player.color,
                int(self.buffers['player_status'][i, 3]),  # checkpoints reached
            )
            for i, player in enumerate(self.players.values())
        ]

        for i, (_, dist, team, speed, col, nch) in enumerate(
            sorted(status, reverse=True)[: self.scoreboard_max_players]
        ):
            self.player_boxes[i].setText(
                f'<div style="color:{col}">&#9632;</div> {i+1}. '
                f'{team[:config.max_name_length]}: {int(dist)} km, '
                f'{int(speed)} km/h [{nch}]'
            )

    def update(self):
        if self.buffers['game_flow'][0]:
            return
        clock_time = time.time()
        self.update_wind_tracers()
        self.update_player_positions()
        if (clock_time - self.last_time_update) > config.time_update_interval:
            self.update_scoreboard()
            self.last_time_update = clock_time

    def update_leaderboard(self, scores, fastest_times):
        sorted_scores = dict(
            sorted(scores.items(), key=lambda item: item[1], reverse=True)
        )
        for i, (name, score) in enumerate(
            list(sorted_scores.items())[: self.scoreboard_max_players]
        ):
            self.score_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f'{i+1}. {name[:config.max_name_length]}: {score}'
            )

        sorted_times = dict(sorted(fastest_times.items(), key=lambda item: item[1]))
        time_list = list(enumerate(sorted_times.items()))
        for i, (name, t) in time_list[:3]:
            try:
                time = str(datetime.timedelta(seconds=int(t)))[2:]
            except OverflowError:
                time = "None"
            self.fastest_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f'{i+1}. {name[:config.max_name_length]}: {time}'
            )

    def run(self):
        main_window = QMainWindow()
        main_window.setWindowTitle("Vendée Globe")
        main_window.setGeometry(100, 100, 1280, 720)

        # Create a central widget to hold the two widgets
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout(central_widget)

        # Create the first widget with vertical checkboxes
        widget1 = QWidget()
        layout.addWidget(widget1)
        widget1_layout = QVBoxLayout(widget1)
        widget1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget1.setMinimumWidth(int(main_window.width() * 0.2))

        self.time_label = QLabel("Time left:")
        widget1_layout.addWidget(self.time_label)
        self.tracer_checkbox = QCheckBox("Wind tracers", checked=True)
        self.tracer_checkbox.stateChanged.connect(self.toggle_wind_tracers)
        widget1_layout.addWidget(self.tracer_checkbox)

        thickness_slider = QSlider(Qt.Horizontal)
        thickness_slider.setMinimum(1)
        thickness_slider.setMaximum(10)
        thickness_slider.setSingleStep(1)
        thickness_slider.setTickInterval(1)
        thickness_slider.setTickPosition(QSlider.TicksBelow)
        thickness_slider.setValue(int(self.tracers.size))
        thickness_slider.valueChanged.connect(self.set_tracer_thickness)
        widget1_layout.addWidget(thickness_slider)

        texture_checkbox = QCheckBox("High contrast", checked=False)
        widget1_layout.addWidget(texture_checkbox)
        texture_checkbox.stateChanged.connect(self.toggle_texture)

        stars_checkbox = QCheckBox("Background stars", checked=True)
        widget1_layout.addWidget(stars_checkbox)
        stars_checkbox.stateChanged.connect(self.toggle_stars)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        widget1_layout.addWidget(separator)

        self.player_boxes = {}
        for i in range(min(len(self.players), self.scoreboard_max_players)):
            self.player_boxes[i] = QLabel("")
            widget1_layout.addWidget(self.player_boxes[i])
        widget1_layout.addStretch()

        layout.addWidget(self.window)
        self.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        widget2 = QWidget()
        layout.addWidget(widget2)
        widget2_layout = QVBoxLayout(widget2)
        widget2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget2.setMinimumWidth(int(main_window.width() * 0.08))
        widget2_layout.addWidget(QLabel("Leader board"))
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        widget2_layout.addWidget(separator)
        widget2_layout.addWidget(QLabel("Scores:"))
        self.score_boxes = {}
        for i in range(min(len(self.players), self.scoreboard_max_players)):
            self.score_boxes[i] = QLabel("")
            widget2_layout.addWidget(self.score_boxes[i])
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        widget2_layout.addWidget(separator)
        widget2_layout.addWidget(QLabel("Fastest finish:"))
        self.fastest_boxes = {}
        for i in range(3):
            self.fastest_boxes[i] = QLabel("")
            widget2_layout.addWidget(self.fastest_boxes[i])
        widget2_layout.addStretch()
        self.update_leaderboard(
            read_scores(self.players.keys(), test=self.test), self.fastest_times
        )

        main_window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        # self.initialize_time()
        self.timer.setInterval(1000 // config.fps)
        self.timer.start()
        pg.exec()

        self.buffers['game_flow'][1] = 1
