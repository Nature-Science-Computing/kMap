# Python Imports
from abc import abstractmethod

# PyQt5 Imports
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QCheckBox, QDoubleSpinBox, QWidget, QTabWidget


class CenteredLabel(QLabel):

    def __init__(self, *args, **kwargs):

        super(CenteredLabel, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)


class UseCheckBox(QCheckBox):

    def __init__(self, *args, **kwargs):

        super(UseCheckBox, self).__init__(*args, **kwargs)

        self.setChecked(True)


class AngleSpinBox(QDoubleSpinBox):

    def __init__(self, value, objectname, *args, **kwargs):

        super(AngleSpinBox, self).__init__(*args, **kwargs)

        self.setSuffix('°')
        self.setMinimum(-90)
        self.setMaximum(90)
        self.setValue(value)
        self.setDecimals(1)
        self.setSingleStep(1)
        self.setKeyboardTracking(False)
        self.setAlignment(Qt.AlignHCenter)
        self.setObjectName(objectname)


class WeightSpinBox(QDoubleSpinBox):

    def __init__(self, *args, value=1, **kwargs):

        super(WeightSpinBox, self).__init__(*args, **kwargs)

        self.setMinimum(0)
        self.setMaximum(99999.9)
        self.setValue(value)
        self.setDecimals(1)
        self.setSingleStep(0.1)
        self.setKeyboardTracking(False)
        self.setAlignment(Qt.AlignHCenter)
        self.setObjectName('weight')

class BackgroundSpinBox(QDoubleSpinBox):

    def __init__(self, *args, value=0, **kwargs):

        super(BackgroundSpinBox, self).__init__(*args, **kwargs)

        self.setMinimum(0)
        self.setMaximum(99999.9)
        self.setValue(value)
        self.setDecimals(1)
        self.setSingleStep(0.1)
        self.setKeyboardTracking(False)
        self.setAlignment(Qt.AlignHCenter)
        self.setObjectName('background')

class EnergySpinBox(QDoubleSpinBox):

    def __init__(self, *args, value=30, **kwargs):

        super(EnergySpinBox, self).__init__(*args, **kwargs)

        self.setSuffix('  eV')
        self.setMinimum(5)
        self.setMaximum(150)
        self.setValue(value)
        self.setDecimals(1)
        self.setSingleStep(0.1)
        self.setKeyboardTracking(False)
        self.setAlignment(Qt.AlignHCenter)
        self.setObjectName('energy')


class FixedSizeWidget(QWidget):

    def __init__(self, width, ratio, *args, **kwargs):

        super(FixedSizeWidget, self).__init__()

        height = width * ratio
        self.resize(width, height)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)


class AspectWidget(QWidget):

    def __init__(self, *args, ratio=0, **kwargs):

        self.ratio = ratio

        super().__init__(*args, **kwargs)

    def set_ratio(self, ratio):

        self.ratio = ratio

    def heightForWidth(self, width):

        return int(width / self.ratio)

    def widthForHeight(self, height):

        return int(height * self.ratio)

    def resizeEvent(self, event):
        '''BUG: For unknown reasons the resizeEvent is called multiple
        times with outdated sizes, thus if the user lowers the side that
        is too large, it will not update correctly.'''
        event.ignore()

        if self.ratio == 0:
            return

        old_width = event.oldSize().width()
        old_height = event.oldSize().height()
        new_width = event.size().width()
        new_height = event.size().height()

        if old_width == new_width:
            if old_height == new_height:
                # No change
                return

            else:
                # Only height changed -> use height
                height = new_height
                width = self.widthForHeight(height)

        else:
            if old_height == new_height:
                # Only width changed -> use width
                width = new_width
                height = self.heightForWidth(width)

            else:
                # Both changed -> use larger one
                if new_width >= new_height:
                    # Width is larger
                    width = new_width
                    height = self.heightForWidth(width)

                else:
                    # Height is larger
                    height = new_height
                    width = self.widthForHeight(height)

        self.blockSignals(True)
        self.resize(width, height)
        self.blockSignals(False)


class Tab(QTabWidget):

    close_requested = pyqtSignal()

    def __init__(self, *args, **kwargs):

        self.title = None

        super(Tab, self).__init__(*args, **kwargs)

    def get_title(self):

        return self.title

    def set_title(self, title):

        self.title = title

    def closeEvent(self, event):

        self.close_requested.emit()
        self.deleteLater()
        event.accept()
