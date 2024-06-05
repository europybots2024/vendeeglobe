# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F405
import time
from typing import Any, Dict, Optional, List

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from matplotlib.colors import to_rgba
from OpenGL.GL import *  # noqa
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem


from . import config
from . import utils as ut
from .core import Location, Checkpoint
from .map import Map
from .player import Player
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

        theta = np.linspace(0, np.pi, 25, dtype="float32")
        phi = np.linspace(0, 2 * np.pi, 49, dtype="float32")
        t_n = theta / np.pi
        p_n = phi / (2 * np.pi)

        phi_grid, theta_grid = np.meshgrid(phi, theta, indexing="ij")
        x, y, z = ut.to_xyz(phi_grid, theta_grid, gl=True)

        glBegin(GL_QUADS)
        for j in range(len(theta) - 1):
            for i in range(len(phi) - 1):
                glTexCoord2f(p_n[i], t_n[j])
                glVertex3f(x[i, j], y[i, j], z[i, j])
                glTexCoord2f(p_n[i], t_n[j + 1])
                glVertex3f(x[i, j + 1], y[i, j + 1], z[i, j + 1])
                glTexCoord2f(p_n[i + 1], t_n[j + 1])
                glVertex3f(x[i + 1, j + 1], y[i + 1, j + 1], z[i + 1, j + 1])
                glTexCoord2f(p_n[i + 1], t_n[j])
                glVertex3f(x[i + 1, j], y[i + 1, j], z[i + 1, j])

        glEnd()
        glDisable(GL_TEXTURE_2D)


"""
Use GLImageItem to display image data on rectangular planes.

In this example, the image data is sampled from a volume and the image planes
placed as if they slice through the volume.
"""


def _make_course_preview(course_preview: List[Checkpoint]) -> tuple:
    course_preview = [
        Checkpoint(
            latitude=config.start.latitude,
            longitude=config.start.longitude,
            radius=5,
        )
    ] + course_preview
    ind = 0
    lats = [config.start.latitude]
    lons = [config.start.longitude]
    while ind < len(course_preview):
        lat = lats[-1]
        lon = lons[-1]
        ch = course_preview[ind]
        if (
            ut.distance_on_surface(
                longitude1=lon,
                latitude1=lat,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            < ch.radius
        ):
            ind += 1
        else:
            heading = ut.goto(
                origin=Location(
                    latitude=lat,
                    longitude=lon,
                ),
                to=Location(
                    latitude=ch.latitude,
                    longitude=ch.longitude,
                ),
            )
            h = heading * np.pi / 180.0
            v = np.array([np.cos(h), np.sin(h)]) * 5.0
            d = [ut.lon_degs_from_length(v[0], lat), ut.lat_degs_from_length(v[1])]
            new_lat, new_lon = ut.wrap(lat=lat + d[1], lon=lon + d[0])
            lats.append(new_lat)
            lons.append(new_lon)

    lats = np.array(lats).ravel()
    lons = np.array(lons).ravel()
    x, y, z = ut.to_xyz(ut.lon_to_phi(lons), ut.lat_to_theta(lats))
    line = gl.GLLinePlotItem(
        pos=np.array([x, y, z]).T,
        color=(255, 0, 0, 255),
        width=2,
        antialias=True,
    )
    line.setGLOptions("opaque")

    lats = np.array([ch.latitude for ch in course_preview])
    lons = np.array([ch.longitude for ch in course_preview])
    lats, lons = ut.wrap(lat=lats, lon=lons)
    x, y, z = ut.to_xyz(ut.lon_to_phi(lons), ut.lat_to_theta(lats))
    vertices = gl.GLScatterPlotItem(
        pos=np.array([x, y, z]).T,
        color=(255, 0, 128, 255),
        size=8,
        pxMode=True,
    )
    vertices.setGLOptions("opaque")
    return line, vertices


class Graphics:
    def __init__(
        self,
        game_map: Map,
        weather: Weather,
        players: Dict[str, Player],
        course_preview: Optional[List[Checkpoint]] = None,
    ):
        t0 = time.time()
        print("Composing graphics...", end=" ", flush=True)
        self.app = pg.mkQApp("Vendee Globe")
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle("Vendee Globe")
        self.window.setCameraPosition(
            distance=config.map_radius * 4,
            elevation=config.start.latitude,
            azimuth=180 + config.start.longitude,
        )

        self.default_texture = np.fliplr(np.transpose(game_map.array, axes=[1, 0, 2]))
        self.high_contrast_texture = np.transpose(
            game_map.high_contrast_texture, axes=[1, 0, 2]
        )
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

        # Add tracers
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(weather.tracer_lon.ravel()),
            ut.lat_to_theta(weather.tracer_lat.ravel()),
        )
        self.default_tracer_colors = weather.tracer_colors
        self.high_contrast_tracer_colors = weather.tracer_colors.copy()
        self.high_contrast_tracer_colors[..., :3] *= 0.8
        self.tracers = gl.GLScatterPlotItem(
            pos=np.array([x, y, z]).T,
            color=self.default_tracer_colors,
            size=2,
            pxMode=True,
        )
        # self.tracers.setGLOptions("opaque")
        self.tracers.setGLOptions("translucent")
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
        self.labels = {}
        for i, (name, player) in enumerate(players.items()):
            x, y, z = ut.to_xyz(
                ut.lon_to_phi(player.longitude),
                ut.lat_to_theta(player.latitude),
            )
            pos = np.array([[x], [y], [z]]).T
            self.tracks[name] = {
                "pos": pos,
                "artist": gl.GLLinePlotItem(
                    pos=pos, color=tuple(colors[i]), width=4, antialias=True
                ),
            }
            self.tracks[name]["artist"].setGLOptions("opaque")
            self.window.addItem(self.tracks[name]["artist"])

        if course_preview is not None:
            line, vertices = _make_course_preview(course_preview)
            self.window.addItem(line)
            self.window.addItem(vertices)

        print(f"done [{time.time() - t0:.2f} s]")

    def update_wind_tracers(self, tracer_lat: np.ndarray, tracer_lon: np.ndarray):
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(tracer_lon.ravel()),
            ut.lat_to_theta(tracer_lat.ravel()),
        )
        self.tracers.setData(pos=np.array([x, y, z]).T)

    def update_player_positions(self, players: Dict[str, Player]):
        latitudes = np.array([player.latitude for player in players.values()])
        longitudes = np.array([player.longitude for player in players.values()])
        x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))
        self.players.setData(pos=np.array([x, y, z]).T)

        for i, (name, player) in enumerate(players.items()):
            if not player.arrived:
                arr = np.array([x[i], y[i], z[i]])
                pos = np.vstack(
                    [self.tracks[name]["pos"], arr],
                )
                npos = len(pos)
                step = (npos // 1000) if npos > 1000 else 1
                self.tracks[name]["artist"].setData(pos=pos[::step])
                self.tracks[name]["pos"] = pos

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
