from app.window.ui_pulse_window import Ui_PulseWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
)


class PulseView(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_PulseWindow()
        self.ui.setupUi(self)

        self.build_sliders(4)

    def build_sliders(self, n):
        groupbox = QGroupBox("Channel Gain")
        group_layout = QHBoxLayout()
        groupbox.setLayout(group_layout)

        for i in range(n):
            col = QVBoxLayout()

            label = QLabel(f"Ch {i + 1}")
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(0, 100)
            slider.setValue(50)

            col.addWidget(label)
            col.addWidget(slider)

            group_layout.addLayout(col)

        self.ui.verticalLayout.addWidget(groupbox)
