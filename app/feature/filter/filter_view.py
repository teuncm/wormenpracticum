from math import floor, log

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.feature.filter.filter_config import FilterConfig
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom


class FilterView(QWidget):
    """Edit filters beside a live preview of the filtered recording."""

    apply_requested = Signal()
    settings_changed = Signal()
    channel_changed = Signal()
    _cutoff_steps = 300

    def __init__(self):
        super().__init__()

        self.cutoff = QDoubleSpinBox()
        self.cutoff.setRange(0, 100_000)
        self.cutoff.setSuffix(" Hz")
        self.cutoff.setSpecialValueText("Off")

        self.cutoff_slider = QSlider(Qt.Orientation.Horizontal)
        self.cutoff_slider.setAccessibleName("Low-pass cutoff")
        self.cutoff_slider.setRange(0, self._cutoff_steps)
        self._slider_limit_hz = 0.0

        self.suppress_50hz = QCheckBox("Suppress 50 Hz interference")
        self.remove_dc = QCheckBox("Remove DC offset")

        self.channel_selector = QComboBox()
        self.channel_selector.setAccessibleName("Preview channel")

        self.apply_button = QPushButton("Apply filters")
        self.status = QLabel()
        self.status.setWordWrap(True)

        settings_title = QLabel("Filter settings")
        settings_title.setObjectName("title_filter_settings")
        settings = QFormLayout()
        settings.addRow("Preview channel", self.channel_selector)
        settings.addRow("Low-pass cutoff", self.cutoff)
        settings.addRow(self.cutoff_slider)
        settings.addRow(self.suppress_50hz)
        settings.addRow(self.remove_dc)
        settings.addRow(self.apply_button)

        controls = QVBoxLayout()
        controls.addWidget(settings_title)
        controls.addLayout(settings)
        controls.addWidget(self.status)
        controls.addStretch()

        preview_title = QLabel("Filtered signal")
        preview_title.setObjectName("title_filter_preview")
        frame, self.plot = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.preview_curve = self.plot.plot(pen="#2166ac", connect="finite")
        self.plot.setDownsampling(auto=True, mode="peak")

        visuals = QVBoxLayout()
        visuals.addWidget(preview_title)
        visuals.addWidget(frame, 1)

        layout = QHBoxLayout(self)
        layout.addLayout(controls)
        layout.addLayout(visuals)
        setup_ui_custom(self)

        self.apply_button.clicked.connect(self.apply_requested.emit)
        self.cutoff_slider.valueChanged.connect(self._cutoff_dragged)
        self.cutoff.valueChanged.connect(self._cutoff_changed)
        self.suppress_50hz.toggled.connect(
            lambda _checked: self.settings_changed.emit()
        )
        self.remove_dc.toggled.connect(lambda _checked: self.settings_changed.emit())
        self.channel_selector.currentIndexChanged.connect(
            lambda _index: self.channel_changed.emit()
        )

    def set_config(self, config: FilterConfig) -> None:
        # Loading saved settings must not schedule a new filter pass.
        with Blocker(self.cutoff, self.suppress_50hz, self.remove_dc):
            self.cutoff.setValue(config.low_pass_cutoff_hz)
            self.suppress_50hz.setChecked(config.suppress_50hz)
            self.remove_dc.setChecked(config.remove_dc_offset)

        self._sync_cutoff_slider()

    def set_channels(self, channels: list[tuple[str, str]]) -> None:
        selected = self.channel_selector.currentData()

        with Blocker(self.channel_selector):
            self.channel_selector.clear()
            for column, label in channels:
                self.channel_selector.addItem(label, column)
            previous_index = self.channel_selector.findData(selected)
            self.channel_selector.setCurrentIndex(max(0, previous_index))

        self.channel_selector.setEnabled(bool(channels))

    def show_preview(
        self, x: np.ndarray, samples: np.ndarray, *, has_time: bool
    ) -> None:
        """Render the selected trace and fit its axes to the filtered samples."""
        self.plot.setLabel(
            "bottom", "Time" if has_time else "Sample", units="s" if has_time else ""
        )
        self.preview_curve.setData(x, samples)
        self.plot.autoRange()

    def clear_preview(self) -> None:
        self.preview_curve.clear()

    def set_sample_rate(self, rate: float | None) -> None:
        # Reserve the leftmost position for Off; the rest of the scale is logarithmic.
        maximum = min(self.cutoff.maximum(), rate * 0.499) if rate else 0.0
        self._slider_limit_hz = floor(maximum * 100) / 100
        self.cutoff_slider.setEnabled(self._slider_limit_hz >= 0.01)
        self._sync_cutoff_slider()

    @property
    def _slider_floor_hz(self) -> float:
        return min(1.0, self._slider_limit_hz / 10)

    def _cutoff_dragged(self, position: int) -> None:
        cutoff = 0.0
        if position and self._slider_limit_hz >= 0.01:
            fraction = (position - 1) / (self._cutoff_steps - 1)
            floor = self._slider_floor_hz
            cutoff = floor * (self._slider_limit_hz / floor) ** fraction
            cutoff = max(0.01, cutoff)

        # The spin box rounds the cutoff; don't snap the pointer back to that rounded value.
        with Blocker(self.cutoff_slider):
            self.cutoff.setValue(cutoff)

    def _cutoff_changed(self, _value: float) -> None:
        if not self.cutoff_slider.signalsBlocked():
            self._sync_cutoff_slider()
        self.settings_changed.emit()

    def _sync_cutoff_slider(self) -> None:
        cutoff = self.cutoff.value()
        position = 0
        if cutoff and self._slider_limit_hz >= 0.01:
            floor = self._slider_floor_hz
            fraction = log(max(floor, cutoff) / floor) / log(
                self._slider_limit_hz / floor
            )
            position = 1 + round((self._cutoff_steps - 1) * min(1.0, fraction))

        with Blocker(self.cutoff_slider):
            self.cutoff_slider.setValue(position)

    def to_config(self) -> FilterConfig:
        return FilterConfig(
            self.cutoff.value(),
            self.suppress_50hz.isChecked(),
            self.remove_dc.isChecked(),
        )
