import numpy as np
from app.model.filter.filters import lowpass_filter
from app.view.view_helpers import create_plot_widget
from app.window.ui_filter_window import Ui_FilterWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QSlider, QWidget

CUTOFF_EPSILON_HZ = 0.01


class FilterView(QWidget):
    def __init__(self):
        super().__init__()

        self.sample_rate = 1000

        self.ui = Ui_FilterWindow()
        self.ui.setupUi(self)

        self.setup_widgets()
        self.generate_signal()
        self.plot_signals()

    def generate_signal(self):
        self.ts, self.original_signal = self.signal_generator(
            frequency=2, noise_amplitude=0.2
        )

    def signal_generator(self, frequency, noise_amplitude):
        ts = np.linspace(0, 1, self.sample_rate, endpoint=False)
        signal = np.sin(2 * np.pi * frequency * ts)
        noise = noise_amplitude * np.random.normal(size=ts.shape)

        return ts, signal + noise

    def setup_widgets(self):
        frame, plot = create_plot_widget(
            title="Before and after filtering",
            x_label="Time",
            x_units="s",
            y_label="Voltage",
            y_units="V",
        )

        self.ui.plotLayout.addWidget(frame)
        self.plotWidget = plot
        self.legend = self.plotWidget.addLegend(offset=(10, 10))
        self.legend.setBrush((255, 255, 255, 230))
        self.legend.setPen((60, 60, 60, 220))

        self.lowpass_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.lowpass_strength_slider.setRange(0, 100)
        self.lowpass_strength_slider.setValue(50)
        self.lowpass_strength_value = QLabel()
        self.filter_enabled_checkbox = QCheckBox("Enabled")
        self.filter_enabled_checkbox.setChecked(True)
        self.lowpass_strength_slider.valueChanged.connect(
            lambda _value: self.plot_signals()
        )
        self.filter_enabled_checkbox.toggled.connect(
            lambda _checked: self.plot_signals()
        )
        self.ui.formLayout.addRow("Filter", self.filter_enabled_checkbox)
        self.ui.formLayout.addRow("Low-pass strength", self.lowpass_strength_slider)
        self.ui.formLayout.addRow("Cutoff (Hz)", self.lowpass_strength_value)

    def get_lowpass_cutoff_hz(self) -> float:
        """Map slider [0..100] to cutoff Hz using log scale for finer low-end control."""
        slider_min = self.lowpass_strength_slider.minimum()
        slider_max = self.lowpass_strength_slider.maximum()
        slider_value = self.lowpass_strength_slider.value()

        # Define the cutoff frequency range to be above 0 and below nyquist frequency, with some epsilon margin.
        min_cutoff_hz = CUTOFF_EPSILON_HZ
        nyquist_hz = self.sample_rate / 2.0
        max_cutoff_hz = max(min_cutoff_hz, nyquist_hz - CUTOFF_EPSILON_HZ)

        t = (slider_value - slider_min) / (slider_max - slider_min)
        return float(min_cutoff_hz * ((max_cutoff_hz / min_cutoff_hz) ** t))

    def plot_signals(self):
        cutoff_hz = self.get_lowpass_cutoff_hz()
        self.lowpass_strength_value.setText(f"{cutoff_hz:.2f}")

        if self.filter_enabled_checkbox.isChecked():
            filter = lowpass_filter(
                sample_rate=self.sample_rate, cutoff_hz=cutoff_hz, order=4
            )
            filtered_signal = filter(self.original_signal)
        else:
            filtered_signal = self.original_signal

        self.plotWidget.clear()
        self.plotWidget.plot(
            self.ts,
            self.original_signal,
            pen={
                "color": (150, 150, 150, 150),
                "width": 1,
                "style": Qt.PenStyle.DotLine,
            },
            name="Original",
        )
        self.plotWidget.plot(
            self.ts,
            filtered_signal,
            pen={
                "color": (0, 100, 200, 255),
                "width": 2,
                "style": Qt.PenStyle.SolidLine,
            },
            name="Filtered",
        )
