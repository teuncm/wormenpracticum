from app.view.symbols import translate_symbols
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QWidget,
)


class PulseSegmentWidget(QWidget):
    segmentChanged = Signal()

    def __init__(self):
        super().__init__()

        formLayout = QFormLayout(self)

        self.spinboxes = {}

        params = {
            "amplitude_v": (0.8, -1.0, 1.0, 0.1),
            "phase_s": (0.2, 0.0, 1.0, 0.1),
            "rest_s": (0.5, 0.0, 1.0, 0.1),
            "delta_amplitude_v": (0.0, -1.0, 1.0, 0.05),
            "delta_phase_s": (0.0, -1.0, 1.0, 0.05),
            "delta_rest_s": (0.0, -1.0, 1.0, 0.05),
        }

        for name, (default_val, min_val, max_val, step) in params.items():
            spin = QDoubleSpinBox()
            spin.setRange(min_val, max_val)
            spin.setSingleStep(step)
            spin.setDecimals(3)
            spin.setValue(default_val)

            spin.valueChanged.connect(self.segmentChanged)

            formLayout.addRow(translate_symbols(name), spin)

            self.spinboxes[name] = spin
