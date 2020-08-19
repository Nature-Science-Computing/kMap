from itertools import chain
import numpy as np

from pyqtgraph.opengl import (
    GLViewWidget, GLGridItem, GLLinePlotItem, MeshData, GLMeshItem)
from pyqtgraph import isosurface

from kmap.controller.pyqtgraphplot import PyQtGraphPlot
from kmap.library.qwidgetsub import FixedSizeWidget
from kmap.library.misc import get_rotation_axes


class MiniKSpacePlot(FixedSizeWidget, PyQtGraphPlot):

    def __init__(self, *args, **kwargs):

        width = 250
        self.ratio = 1
        self.ID = None

        super(MiniKSpacePlot, self).__init__(300, 1, *args, **kwargs)
        self._setup()

    def plot(self, plot_data, ID):

        self.ID = ID

        PyQtGraphPlot.plot(self, plot_data)

    def _setup(self):

        PyQtGraphPlot._setup(self)

        self.ui.histogram.hide()
        self.view.showAxis('bottom', show=False)
        self.view.showAxis('left', show=False)
        self.view.showAxis('top', show=False)
        self.view.showAxis('right', show=False)
        self.view.setAspectLocked(lock=True, ratio=self.ratio)


class MiniRealSpacePlot(GLViewWidget):

    def __init__(self, *args, **kwargs):

        self.options = None
        self.grid = None
        self.bonds = []
        self.photon = None
        self.photon_parameters = ['p', 0, 0]
        self.mesh = []
        self.orbital = None
        self.orientation = [0, 0, 0]

        super(MiniRealSpacePlot, self).__init__(*args, **kwargs)
        self._setup()

        self.show()

    def set_orbital(self, orbital):

        self.orbital = orbital
        self.orientation = [0, 0, 0]

        self.refresh_plot()

    def set_options(self, options):

        self.options = options
        self._connect()

    def rotate_orbital(self, phi=0, theta=0, psi=0):

        old_axes = get_rotation_axes(*self.orientation[:2])
        new_axes = get_rotation_axes(phi, theta)
        for item in chain(self.bonds, self.mesh):
            # Undo current orientation
            self._rotate_item(item, old_axes, *self.orientation,
                              backward=True)
            # Actuallly rotate to new orientation
            self._rotate_item(item, new_axes, phi, theta, psi, backward=False)

        self.orientation = [phi, theta, psi]

    def rotate_photon(self, polarization='p', alpha=0, beta=0):

        if self.photon is not None:
            self.removeItem(self.photon)
            self.photon = None

        self.photon_parameters = [polarization, alpha, beta]
        self._refresh_photon()

    def refresh_plot(self):

        self._refresh_grid()
        self._refresh_bonds()
        self._refresh_photon()
        self._refresh_mesh()

    def reset_camera(self, distance=75, elevation=90, azimuth=-90):

        # View from top
        self.setCameraPosition(distance=distance, elevation=elevation,
                               azimuth=azimuth)

    def toggle_show_grid(self, state):

        if self.grid is not None:
            self.grid.setVisible(state)

    def toggle_show_bonds(self, state):

        if self.bonds:
            for bond in self.bonds:
                bond.setVisible(state)

    def toggle_show_photon(self, state):

        if self.photon is not None:
            self.photon.setVisible(state)

    def toggle_show_mesh(self, state):

        if self.mesh:
            for mesh in self.mesh:
                mesh.setVisible(state)

    def _refresh_mesh(self):

        if self.mesh:
            for mesh in self.mesh:
                self.removeItem(mesh)

            self.mesh = []

        if self.orbital is None or not self.options.is_show_mesh():
            return

        data = self.orbital.psi['data']
        plus_mesh = self._get_iso_mesh(data, 'red', 1)
        minus_mesh = self._get_iso_mesh(data, 'blue', -1)
        self.addItem(plus_mesh)
        self.addItem(minus_mesh)

        self.mesh = [plus_mesh, minus_mesh]

        # Updating the mesh after iso val change would leave it
        # unrotated
        axes = get_rotation_axes(*self.orientation[:2])
        for item in self.mesh:
            self._rotate_item(item, axes, *self.orientation, backward=False)

    def _refresh_bonds(self):

        if self.bonds:
            for bond in self.bonds:
                self.removeItem(bond)

            self.bonds = []

        if self.orbital is None or not self.options.is_show_bonds():
            return

        color = (1, 1, 0.5, 0.5)

        for bond in self.orbital.get_bonds():
            new_bond = GLLinePlotItem(pos=bond, color=color,
                                      width=5, antialias=True)
            self.bonds.append(new_bond)

            self.addItem(new_bond)

    def _refresh_photon(self):

        polarization, alpha, beta = self.photon_parameters
        print(polarization, alpha, beta)
        if not self.options.is_show_photon():
            return

        color = (1, 1, 0.5, 0.5)

        some_line_test = GLLinePlotItem(pos=np.array([[0,0,0],[10,10,10]]), color=color,
                                        width=5, antialias=True)
        self.photon = some_line_test

        self.addItem(some_line_test)


    def _refresh_grid(self):

        if self.grid is not None:
            self.removeItem(self.grid)
            self.grid = None

        if self.orbital is None or not self.options.is_show_grid():
            return

        self.grid = GLGridItem()
        dx, dy, dz = [self.orbital.psi[key] for key in ['dx', 'dy', 'dz']]
        self.grid.scale(1 / dx, 1 / dy, 1 / dz)
        self.addItem(self.grid)

    def _rotate_item(self, item, axes, phi, theta, psi, backward=False):

        if backward:
            # Undo Rotation in reverse order
            item.rotate(psi, axes[2][0], axes[2][1], axes[2][2], local=True)
            item.rotate(theta, axes[1][0], axes[1][1], axes[1][2], local=True)
            item.rotate(phi, axes[0][0], axes[0][1], axes[0][2], local=True)

        else:
            item.rotate(-phi, axes[0][0], axes[0][1], axes[0][2], local=True)
            item.rotate(-theta, axes[1][0], axes[1][1], axes[1][2], local=True)
            item.rotate(-psi, axes[2][0], axes[2][1], axes[2][2], local=True)

    def _get_iso_mesh(self, data, color, sign):

        iso_val = sign * self.options.get_iso_val()
        vertices, faces = isosurface(data, iso_val * data.max())
        nx, ny, nz = data.shape

        # Center Isosurface around Origin
        vertices[:, 0] = vertices[:, 0] - nx / 2
        vertices[:, 1] = vertices[:, 1] - ny / 2
        vertices[:, 2] = vertices[:, 2] - nz / 2

        mesh_data = MeshData(vertexes=vertices, faces=faces)
        colors = np.zeros((mesh_data.faceCount(), 4), dtype=float)
        # Sets color to Red (RGB, 0 = red, 1 = green, 2 = blue)
        if color == 'red':
            colors[:, 0] = 1.0
            colors[:, 1] = 0.2
            colors[:, 2] = 0.2

        elif color == 'blue':
            colors[:, 0] = 0.2
            colors[:, 1] = 0.2
            colors[:, 2] = 1.0
        # Transparency (I guess)
        colors[:, 3] = 1
        mesh_data.setFaceColors(colors)

        mesh = GLMeshItem(meshdata=mesh_data, smooth=True, shader='edgeHilight')
        mesh.setGLOptions('translucent')

        return mesh

    def _setup(self):

        # Set Fixed Size. Due to some unknown reason subclassing from a
        # second class like FixedSizeWidget while also
        # subclassing from gl.GLViewWidget throws error
        width = 250
        ratio = 1
        height = width * ratio
        self.resize(width, height)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

        self.reset_camera()

    def _connect(self):

        self.options.set_camera.connect(self.reset_camera)
        self.options.show_grid_changed.connect(self.toggle_show_grid)
        self.options.show_mesh_changed.connect(self.toggle_show_mesh)
        self.options.show_bonds_changed.connect(self.toggle_show_bonds)
        self.options.show_photon_changed.connect(self.toggle_show_photon)
        self.options.iso_val_changed.connect(self._refresh_mesh)
