from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
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
            "amp_v": (1.0, -1.0, 1.0, 0.1),
            "dur_s": (1.0, 0.0, 1.0, 0.1),
            "step_amp_v": (0.0, -1.0, 1.0, 0.1),
            "step_dur_s": (0.0, -1.0, 1.0, 0.1),
        }

        for name, (default_val, min_val, max_val, step) in params.items():
            spin = QDoubleSpinBox()
            spin.setRange(min_val, max_val)
            spin.setSingleStep(step)
            spin.setDecimals(3)
            spin.setValue(default_val)

            spin.valueChanged.connect(self.segmentChanged)

            formLayout.addRow(name, spin)

            self.spinboxes[name] = spin

        self.monophasic_checkbox = QCheckBox("is_monophasic")

        self.monophasic_checkbox.setChecked(False)
        self.monophasic_checkbox.stateChanged.connect(self.segmentChanged)

        formLayout.addRow(self.monophasic_checkbox)
