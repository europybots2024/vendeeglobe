# flake8: noqa F405
import time
from typing import Any, Dict

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from matplotlib.colors import to_rgba
from OpenGL.GL import *  # noqa
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem


from . import config
from . import utils as ut
from .map import MapTextures
from .player import Player
from .utils import array_from_shared_mem
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
