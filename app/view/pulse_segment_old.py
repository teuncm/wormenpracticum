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
            "V": (0.5, 0.0, 1.5, 0.1),
            "PW": (0.2, 0.0, 0.5, 0.01),
            "T": (0.1, 0.0, 1, 0.1),
            "DELTA_V": (0.0, 0.0, 1.0, 0.01),
            "DELTA_PW": (0.0, -1.0, 1.0, 0.01),
            "DELTA_T": (0.0, -100.0, 100.0, 1.0),
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
