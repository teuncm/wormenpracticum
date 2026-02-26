import pyqtgraph as pg
from app.window.ui_pulse_window import Ui_PulseWindow
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
)


class PulseView(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_PulseWindow()
        self.ui.setupUi(self)

        self.ui.pulseWidthSlider.valueChanged.connect(self.update_pulse_width)

        self.plotWidget = pg.PlotWidget()
        layout = QVBoxLayout(self.ui.pulseContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotWidget)

        self.plotWidget.setTitle("Impulse")
        self.plotWidget.setLabel("left", "Voltage", units="V")
        self.plotWidget.setLabel("bottom", "Time", units="s")
        self.plotWidget.setMouseEnabled(x=False, y=False)

    def set_controller(self, controller):
        self.controller = controller

    def update_pulse_width(self, value):
        pulse_width = value / 100.0
        self.plotWidget.clear()
        self.plotWidget.plot(
            [0, pulse_width, pulse_width, 1],
            [0, 0, 1, 1],
            pen=pg.mkPen(color="r", width=2),
            name="Pulse",
        )
