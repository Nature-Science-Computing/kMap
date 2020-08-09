# PyQt5 Imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton

# Own Imports
from kmap.library.misc import orientation_to_euler_angle
from kmap.library.qwidgetsub import (CenteredLabel, UseCheckBox,
                                     AngleSpinBox, WeightSpinBox)


class OrbitalTableRow(QWidget):

    row_removed = pyqtSignal(int)
    parameter_changed = pyqtSignal(int, str, float)
    use_changed = pyqtSignal(int)

    def __init__(self, orbital, orientation, *args, **kwargs):

        self.ID = orbital.ID

        self._setup(orbital, orientation)
        self._connect()

        super(OrbitalTableRow, self).__init__(*args, **kwargs)

    def remove_row(self):

        self.row_removed.emit(self.ID)

    def get_parameters(self):

        weight = self.weight.value()
        phi = self.phi.value()
        theta = self.theta.value()
        psi = self.psi.value()

        return weight, phi, theta, psi

    def get_use(self):

        return self.use.isChecked()

    def change_parameter(self):

        sender = self.sender()

        parameter = sender.objectName()
        value = sender.value()

        self.parameter_changed.emit(self.ID, parameter, value)

    def change_use(self):

        self.use_changed.emit(self.ID)

    def update_parameter_silently(self, parameter, value):

        widgets = [self.weight, self.phi, self.theta, self.psi]

        for widget in widgets:
            if widget.objectName() == parameter:

                widget.blockSignals(True)
                widget.setValue(value)
                widget.blockSignals(False)

    def _setup(self, orbital, orientation):

        self.button = QPushButton('X')
        self.ID_label = CenteredLabel('%i' % orbital.ID)
        self.name_label = CenteredLabel(orbital.name)
        self.weight = WeightSpinBox()

        phi, theta, psi = orientation_to_euler_angle(orientation)
        self.phi = AngleSpinBox(phi, 'phi')
        self.theta = AngleSpinBox(theta, 'theta')
        self.psi = AngleSpinBox(psi, 'psi')

        self.use = UseCheckBox()

    def _connect(self):

        self.button.clicked.connect(self.remove_row)

        self.weight.valueChanged.connect(self.change_parameter)
        self.phi.valueChanged.connect(self.change_parameter)
        self.theta.valueChanged.connect(self.change_parameter)
        self.psi.valueChanged.connect(self.change_parameter)

        self.use.stateChanged.connect(self.change_use)
