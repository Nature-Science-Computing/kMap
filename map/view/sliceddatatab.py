from map.ui.sliceddatatab_ui import SlicedDataTabUI
from PyQt5.QtWidgets import QWidget


class SlicedDataTab(QWidget, SlicedDataTabUI):

    def __init__(self, model, data):

        super().__init__()

        self.setupUi(model)

        self.plot_item.plot(data.slice_from_idx(0))