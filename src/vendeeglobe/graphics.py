# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Dict

import numpy as np
from OpenGL.GL import *  # noqa
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import datetime
from matplotlib.colors import to_rgba

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication
import sys

from pyqtgraph.Qt import QtWidgets

from . import config
from .map import Map
from .player import Player
from . import utils as ut
from .weather import Weather


class GLTexturedSphereItem(GLGraphicsItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem.GLGraphicsItem>`

    Displays image data as a textured quad.
    """

    def __init__(
        self,
        data: np.ndarray,
        smooth: bool = False,
        glOptions: str = "translucent",
        parentItem: Any = None,
    ):
        """
        **Arguments:**
        data:
            Volume data to be rendered. *Must* be 3D numpy array (x, y, RGBA) with
            dtype=ubyte. (See functions.makeRGBA)
        smooth:
            If True, the volume slices are rendered with linear interpolation
        """

        self.smooth = smooth
        self._needUpdate = False
        super().__init__(parentItem=parentItem)
        self.setData(data)
        self.setGLOptions(glOptions)
        self.texture = None

    def initializeGL(self):
        if self.texture is not None:
            return
        glEnable(GL_TEXTURE_2D)
        self.texture = glGenTextures(1)

    def setData(self, data: np.ndarray):
        self.data = data
        self._needUpdate = True
        self.update()

    def _updateTexture(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        if self.smooth:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        # glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)
        shape = self.data.shape

        ## Test texture dimensions first
        glTexImage2D(
            GL_PROXY_TEXTURE_2D,
            0,
            GL_RGBA,
            shape[0],
            shape[1],
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            None,
        )
        if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D, 0, GL_TEXTURE_WIDTH) == 0:
            raise Exception(
                "OpenGL failed to create 2D texture (%dx%d); too large for this hardware."
                % shape[:2]
            )

        data = np.ascontiguousarray(self.data.transpose((1, 0, 2)))
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            shape[0],
            shape[1],
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data,
        )
        glDisable(GL_TEXTURE_2D)

    def paint(self):
        if self._needUpdate:
            self._updateTexture()
            self._needUpdate = False
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        self.setupGLState()

        glColor4f(1, 1, 1, 1)

        theta = np.linspace(0, np.pi, 32, dtype="float32")
        phi = np.linspace(0, 2 * np.pi, 64, dtype="float32")
        t_n = theta / np.pi
        p_n = phi / (2 * np.pi)

        glBegin(GL_QUADS)
        for j in range(len(theta) - 1):
            for i in range(len(phi) - 1):
                xyz_nw = ut.to_xyz(phi[i], theta[j], gl=True)
                xyz_sw = ut.to_xyz(phi[i], theta[j + 1], gl=True)
                xyz_se = ut.to_xyz(phi[i + 1], theta[j + 1], gl=True)
                xyz_ne = ut.to_xyz(phi[i + 1], theta[j], gl=True)

                glTexCoord2f(p_n[i], t_n[j])
                glVertex3f(xyz_nw[0], xyz_nw[1], xyz_nw[2])
                glTexCoord2f(p_n[i], t_n[j + 1])
                glVertex3f(xyz_sw[0], xyz_sw[1], xyz_sw[2])
                glTexCoord2f(p_n[i + 1], t_n[j + 1])
                glVertex3f(xyz_se[0], xyz_se[1], xyz_se[2])
                glTexCoord2f(p_n[i + 1], t_n[j])
                glVertex3f(xyz_ne[0], xyz_ne[1], xyz_ne[2])

        glEnd()
        glDisable(GL_TEXTURE_2D)


"""
Use GLImageItem to display image data on rectangular planes.

In this example, the image data is sampled from a volume and the image planes
placed as if they slice through the volume.
"""


class Graphics:
    def __init__(self, game_map: Map, weather: Weather, players: Dict[str, Player]):
        self.app = pg.mkQApp("Vendee Globe")
        # self.app = QApplication(sys.argv)
        self.window = gl.GLViewWidget()

        self.window.setWindowTitle("Vendee Globe")
        self.window.setCameraPosition(distance=config.map_radius * 4)

        self.default_texture = np.fliplr(np.transpose(game_map.array, axes=[1, 0, 2]))
        # self.high_contrast_texture = np.fliplr(
        #     np.transpose(game_map.high_contrast_texture, axes=[1, 0, 2])
        # )
        self.high_contrast_texture = np.transpose(
            game_map.high_contrast_texture, axes=[1, 0, 2]
        )
        # self.high_contrast_texture = game_map.high_contrast_texture
        self.sphere = GLTexturedSphereItem(self.default_texture)
        self.sphere.setGLOptions("opaque")
        self.window.addItem(self.sphere)

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

        # Add tracers
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(weather.tracer_lon.ravel()),
            ut.lat_to_theta(weather.tracer_lat.ravel()),
        )
        self.default_tracer_colors = weather.tracer_colors
        self.high_contrast_tracer_colors = weather.tracer_colors.copy()
        self.high_contrast_tracer_colors[..., :3] *= 0.9
        self.tracers = gl.GLScatterPlotItem(
            pos=np.array([x, y, z]).T,
            # color=weather.tracer_colors.reshape((-1, 4)),
            color=self.default_tracer_colors,
            size=4,
            pxMode=True,
        )
        # self.tracers.setGLOptions("opaque")
        self.tracers.setGLOptions('translucent')
        self.window.addItem(self.tracers)

        # Add players
        latitudes = np.array([player.latitude for player in players.values()])
        longitudes = np.array([player.longitude for player in players.values()])
        colors = np.array([to_rgba(player.color) for player in players.values()])
        x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))

        self.players = gl.GLScatterPlotItem(
            pos=np.array([x, y, z]).T,
            color=colors,
            size=10,
            pxMode=True,
        )
        self.players.setGLOptions("opaque")
        # self.tracers.setGLOptions('translucent')
        self.window.addItem(self.players)

        self.tracks = {}
        for i, (name, player) in enumerate(players.items()):
            x, y, z = ut.to_xyz(
                ut.lon_to_phi(player.longitude), ut.lat_to_theta(player.latitude)
            )
            pos = np.array([[x], [y], [z]]).T
            self.tracks[name] = {
                'pos': pos,
                'artist': gl.GLLinePlotItem(
                    pos=pos, color=tuple(colors[i]), width=4, antialias=True
                ),
            }
            self.tracks[name]['artist'].setGLOptions("opaque")
            self.window.addItem(self.tracks[name]['artist'])

    def update_wind_tracers(
        self, tracer_lat: np.ndarray, tracer_lon: np.ndarray, reset_colors: bool = False
    ):
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(tracer_lon.ravel()), ut.lat_to_theta(tracer_lat.ravel())
        )
        kwargs = dict(pos=np.array([x, y, z]).T)
        if reset_colors:
            kwargs['color'] = self.default_tracer_colors
        self.tracers.setData(**kwargs)

    def update_player_positions(self, players: Dict[str, Player]):
        latitudes = np.array([player.latitude for player in players.values()])
        longitudes = np.array([player.longitude for player in players.values()])
        x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))
        self.players.setData(pos=np.array([x, y, z]).T)

        for i, name in enumerate(self.tracks):
            pos = np.vstack(
                [self.tracks[name]['pos'], np.array([x[i], y[i], z[i]])],
            )
            npos = len(pos)
            step = (npos // 1000) if npos > 1000 else 1
            self.tracks[name]['artist'].setData(pos=pos[::step])
            self.tracks[name]['pos'] = pos

    def update_time(self, t: float):
        time = str(datetime.timedelta(seconds=int(t)))[2:]
        self.window.setWindowTitle(f"Vendee Globe - Time left: {time} s")

    def hide_wind_tracers(self):
        self.tracers.setData(color=np.zeros_like(self.default_tracer_colors))

    def toggle_texture(self, val):
        if val:
            self.sphere.setData(self.high_contrast_texture)
            self.tracers.setData(color=self.high_contrast_tracer_colors)
        else:
            self.sphere.setData(self.default_texture)
            self.tracers.setData(color=self.default_tracer_colors)
