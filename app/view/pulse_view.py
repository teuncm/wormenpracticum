import pyqtgraph as pg
from app.view.symbols import translate_symbols
from app.window.ui_pulse_window import Ui_PulseWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


class PulseView(QDialog):
    pulseParametersChanged = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_PulseWindow()
        self.ui.setupUi(self)

        layout = QVBoxLayout(self.ui.sliderBox)

        self.spinboxes = {}

        params = {
            "V": (0.0, 2.0, 0.01),
            "PW": (0.0, 1.0, 0.01),
            "T": (0.0, 100.0, 0.1),
            "DELTA_V": (0.0, 1.0, 0.01),
            "DELTA_PW": (-1.0, 1.0, 0.01),
            "DELTA_T": (0.0, 360.0, 1.0),
        }

        for name, (min_val, max_val, step) in params.items():
            row = QHBoxLayout()

            label = QLabel(translate_symbols(name))
            label.setFixedWidth(40)

            spin = QDoubleSpinBox()
            spin.setRange(min_val, max_val)
            spin.setSingleStep(step)
            spin.setDecimals(3)
            spin.setValue(0.0)

            spin.valueChanged.connect(self.pulseParametersChanged)

            row.addWidget(label)
            row.addWidget(spin)

            layout.addLayout(row)

            self.spinboxes[name] = spin

        self.plotWidget = pg.PlotWidget()
        layout = QVBoxLayout(self.ui.pulseContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotWidget)

        self.plotWidget.setTitle("Impulse")
        self.plotWidget.setLabel("left", "Voltage", units="V")
        self.plotWidget.setLabel("bottom", "Time", units="s")
        self.plotWidget.setMouseEnabled(x=False, y=False)

    def update_pulse_width(self, value):
        pulse_width = value / 100.0
        self.plotWidget.clear()
        self.plotWidget.plot(
            [0, pulse_width, pulse_width, 1],
            [0, 0, 1, 1],
            pen=pg.mkPen(color="r", width=2),
            name="Pulse",
        )
