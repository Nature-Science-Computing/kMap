from PyQt5.QtWidgets import QHBoxLayout
from kmap.ui.abstract_ui import AbstractUI
from kmap.view.pyqtgraphplot import PyQtGraphPlot
from kmap.view.crosshair import CrosshairAnnulus

class OrbitalDataTabUI(AbstractUI):

    def _initialize_content(self):

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Plot
        self.plot_item = PyQtGraphPlot()
        main_layout.addWidget(self.plot_item)

        # Crosshair
        self.crosshair = CrosshairAnnulus(self.plot_item)
        main_layout.addWidget(self.crosshair)

    def _initialize_connections(self):

        self.crosshair.crosshair_changed.connect(self.crosshair_changed)