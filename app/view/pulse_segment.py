from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QGridLayout, QLabel, QWidget


class PulseSegmentWidget(QWidget):
    segmentChanged = Signal()

    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel("Base"), 0, 1)
        layout.addWidget(QLabel("Step"), 0, 2)

        self.spinboxes = {}

        params = {
            "Amplitude (V)": ("amp_v", "step_amp_v"),
            "Duration (s)": ("dur_s", "step_dur_s"),
        }

        defaults = {
            "amp_v": (1.0, -1.0, 1.0, 0.1),
            "dur_s": (1.0, 0.0, 1.0, 0.1),
            "step_amp_v": (0.0, -1.0, 1.0, 0.1),
            "step_dur_s": (0.0, -1.0, 1.0, 0.1),
        }

        for row, (label, (base_key, step_key)) in enumerate(params.items(), start=1):
            layout.addWidget(QLabel(label), row, 0)

            for col, key in enumerate([base_key, step_key], start=1):
                default_val, min_val, max_val, step = defaults[key]

                spin = QDoubleSpinBox()
                spin.setRange(min_val, max_val)
                spin.setSingleStep(step)
                spin.setDecimals(3)
                spin.setValue(default_val)

                spin.valueChanged.connect(self.segmentChanged)

                layout.addWidget(spin, row, col)
                self.spinboxes[key] = spin

        self.monophasic_checkbox = QCheckBox("Monophasic")
        self.monophasic_checkbox.stateChanged.connect(self.segmentChanged)

        layout.addWidget(self.monophasic_checkbox, 3, 0, 1, 3)
