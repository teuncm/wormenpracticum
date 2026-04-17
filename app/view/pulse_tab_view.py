from app.constants import (
    DOUBLE_SPIN_MAX_S,
    DOUBLE_SPIN_MAX_V,
    DOUBLE_SPIN_STEP_S,
    DOUBLE_SPIN_STEP_V,
)
from app.view.view_helpers import double_spin_helper
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QGridLayout, QLabel, QWidget


class PulseTabView(QWidget):
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
            "Start (s)": ("start_s", "step_start_s"),
            "Duration (s)": ("dur_s", "step_dur_s"),
        }

        spinbox_configs = {
            "amp_v": (
                0.5,
                -DOUBLE_SPIN_MAX_V,
                DOUBLE_SPIN_MAX_V,
                DOUBLE_SPIN_STEP_V,
            ),
            "start_s": (0.001, 0.0, DOUBLE_SPIN_MAX_S, DOUBLE_SPIN_STEP_S),
            "dur_s": (0.002, 0.0, DOUBLE_SPIN_MAX_S, DOUBLE_SPIN_STEP_S),
            "step_amp_v": (
                0.0,
                -DOUBLE_SPIN_MAX_V,
                DOUBLE_SPIN_MAX_V,
                DOUBLE_SPIN_STEP_V,
            ),
            "step_start_s": (
                0.0,
                -DOUBLE_SPIN_MAX_S,
                DOUBLE_SPIN_MAX_S,
                DOUBLE_SPIN_STEP_S,
            ),
            "step_dur_s": (
                0.0,
                -DOUBLE_SPIN_MAX_S,
                DOUBLE_SPIN_MAX_S,
                DOUBLE_SPIN_STEP_S,
            ),
        }

        for row, (label, (base_key, step_key)) in enumerate(params.items(), start=1):
            layout.addWidget(QLabel(label), row, 0)

            for col, key in enumerate([base_key, step_key], start=1):
                default_val, min_val, max_val, step = spinbox_configs[key]

                spin = QDoubleSpinBox()
                double_spin_helper(spin, default_val, min_val, max_val, step)

                spin.valueChanged.connect(self.segmentChanged)

                layout.addWidget(spin, row, col)
                self.spinboxes[key] = spin

        self.monophasic_checkbox = QCheckBox("Monophasic")
        self.monophasic_checkbox.stateChanged.connect(self.segmentChanged)

        layout.addWidget(self.monophasic_checkbox, 4, 0, 1, 3)