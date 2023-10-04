# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from OpenGL.GL import *  # noqa
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from pyqtgraph.Qt import QtWidgets

from . import config
from . import utils as ut


class GLTexturedSphereItem(GLGraphicsItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem.GLGraphicsItem>`

    Displays image data as a textured quad.
    """

    def __init__(self, data, smooth=False, glOptions="translucent", parentItem=None):
        """

        ==============  =======================================================================================
        **Arguments:**
        data            Volume data to be rendered. *Must* be 3D numpy array (x, y, RGBA) with dtype=ubyte.
                        (See functions.makeRGBA)
        smooth          (bool) If True, the volume slices are rendered with linear interpolation
        ==============  =======================================================================================
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

    def setData(self, data):
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
    def __init__(self, game_map, weather, players):
        # self.map = game_map

        # app = pg.mkQApp("GLImageItem Example")

        # rcheck = QtWidgets.QCheckBox('plot remote')
        # rcheck.setChecked(True)
        # # lcheck = QtWidgets.QCheckBox('plot local')
        # # lplt = pg.PlotWidget()
        # self.layout = pg.LayoutWidget()
        # self.layout.addWidget(rcheck)
        # layout.addWidget(lcheck)
        # layout.addWidget(label)
        # layout.addWidget(lplt, row=2, col=0, colspan=3)
        # layout.resize(800, 800)
        # layout.show()

        self.window = gl.GLViewWidget()

        # w.show()
        self.window.setWindowTitle("Vendee Globe")
        self.window.setCameraPosition(distance=config.map_radius * 4)

        # world_mask = self.map.array.T

        # print('Graphics 1')

        # # world = np.load(f'world{config.map_resolution}.npz')['world'].T
        # world = self.map.array.T
        # # print('Graphics 2')

        # a = np.reshape(world.astype('uint8'), world.shape + (1,))
        # # print('Graphics 3')
        # a = np.broadcast_to(a, world.shape + (4,)) * 255
        # # print('Graphics 4')
        # a[~world] = [0, 0, 100, 255]
        # # print('Graphics 5')
        # a[world] = [100, 140, 46, 255]
        # # print('Graphics 6')

        # # np.savez('world.npz', world=a)
        # # a = np.load('world.npz')['world']
        world = np.fliplr(np.transpose(game_map.array, axes=[1, 0, 2]))

        self.sphere = GLTexturedSphereItem(world)
        # print('Graphics 7')
        self.sphere.setGLOptions("opaque")
        # print('Graphics 8')
        self.window.addItem(self.sphere)
        # print('Graphics 9')

        # self.tracer_lat = np.random.uniform(-90.0, 90.0, size=config.ntracers)
        # self.tracer_lon = np.random.uniform(-180, 180, size=config.ntracers)

        # Add checkpoints
        scl = [0.96, 0.99]
        for i, ch in enumerate(config.checkpoints):
            # x, y, z = ut.to_xyz(
            #     ut.lon_to_phi(ch.longitude),
            #     ut.lat_to_theta(ch.latitude),
            # )
            md = gl.MeshData.cylinder(
                rows=10,
                cols=20,
                radius=[ch['radius'], ch['radius']],
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
            mesh.rotate(np.degrees(ut.lat_to_theta(ch['latitude'])), 0, 1, 0)
            mesh.rotate(np.degrees(ut.lon_to_phi(ch['longitude'])), 0, 0, 1)
            self.window.addItem(mesh)

        # Add tracers
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(weather.tracer_lon.ravel()),
            ut.lat_to_theta(weather.tracer_lat.ravel()),
        )
        self.tracers = gl.GLScatterPlotItem(
            pos=np.array([x, y, z]).T,
            color=weather.tracer_colors.reshape((-1, 4)),
            size=4,
            pxMode=True,
        )
        # self.tracers.setGLOptions("opaque")
        self.tracers.setGLOptions('translucent')
        self.window.addItem(self.tracers)

        # Add players
        latitudes = np.array([player.latitude for player in players.values()])
        longitudes = np.array([player.longitude for player in players.values()])
        colors = np.array([player.color for player in players.values()])
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

        # self.layout.addWidget(self.window, row=0, col=1)

    def update_wind_tracers(self, tracer_lat, tracer_lon, tracer_colors):
        # return
        x, y, z = ut.to_xyz(
            ut.lon_to_phi(tracer_lon.ravel()), ut.lat_to_theta(tracer_lat.ravel())
        )
        self.tracers.setData(
            pos=np.array([x, y, z]).T,
            # color=tracer_colors.reshape((-1, 4))
        )

    def update_player_positions(self, players):
        latitudes = np.array([player.latitude for player in players.values()])
        longitudes = np.array([player.longitude for player in players.values()])
        x, y, z = ut.to_xyz(ut.lon_to_phi(longitudes), ut.lat_to_theta(latitudes))
        self.players.setData(pos=np.array([x, y, z]).T)

        for i, name in enumerate(self.tracks):
            pos = np.vstack(
                [self.tracks[name]['pos'], np.array([x[i], y[i], z[i]])],
            )
            self.tracks[name]['artist'].setData(pos=pos)
            self.tracks[name]['pos'] = pos
