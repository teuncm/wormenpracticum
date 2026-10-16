"""Shared amplitude and pin-baseline layout for analysis plots."""

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget


class VerticalZoomControl(QWidget):
    """Magnify traces logarithmically relative to the user's base amplitude."""

    zoomChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.factor_label = QLabel("1×")
        self.factor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.factor_label)
        upper_label = QLabel("100×")
        upper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(upper_label)
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setAccessibleName("Vertical zoom")
        self.slider.setRange(0, 200)
        self.slider.setValue(0)
        self.slider.setPageStep(10)
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        layout.addWidget(self.slider, 1, Qt.AlignmentFlag.AlignHCenter)
        lower_label = QLabel("1×")
        lower_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lower_label)
        self.setToolTip(
            "Vertical zoom relative to Total visible amplitude. 1× restores that range."
        )
        self.slider.valueChanged.connect(self._zoom_changed)
        self.setEnabled(False)

    @property
    def factor(self) -> float:
        """Return logarithmic magnification from 1 at the bottom to 100 at the top."""
        return 100 ** (self.slider.value() / 200)

    def visible_amplitude(self, base_amplitude: float) -> float:
        """Derive the range from the base value without compounding slider changes."""
        return base_amplitude / self.factor

    def _zoom_changed(self, _value: int) -> None:
        self.factor_label.setText(f"{self.factor:.3g}×")
        self.zoomChanged.emit(self.factor)


def add_vertical_zoom(right_layout, plot_frame: QWidget) -> VerticalZoomControl:
    """Place the common zoom slider on the left side of an analysis plot."""
    row = QHBoxLayout()
    control = VerticalZoomControl()
    row.addWidget(control)
    row.addWidget(plot_frame, 1)
    right_layout.addLayout(row)
    return control


def default_total_amplitude(values: np.ndarray, channel_count: int) -> float:
    """Return a finite default total span that contains centered pin traces.

    Use the largest absolute voltage so constant DC traces remain visible around
    the zero reference. The margin and minimum keep all-NaN and constant data
    usable, while multiplying by the visible channel count preserves per-pin
    spacing as the total span grows.
    """
    numeric = np.asarray(values, dtype=float)
    finite = numeric[np.isfinite(numeric)]
    extent = float(np.max(np.abs(finite))) if finite.size else 0.0
    return max(0.001, 2 * extent * 1.2) * max(1, int(channel_count))


def vertical_pin_layout(
    amplitude: float, channel_count: int
) -> tuple[float, list[float]]:
    """Return equal pin spacing and zero-based offsets for the visible pins."""
    count = max(1, int(channel_count))
    spacing = float(amplitude) / count
    return spacing, [rank * spacing for rank in range(count)]


def apply_vertical_range(
    plot_widget: pg.PlotWidget, amplitude: float, count: int
) -> None:
    """Set a centered total y span and keep future data from rescaling it."""
    visible_count = max(1, int(count))
    plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
    plot_widget.setYRange(
        -amplitude / (2 * visible_count),
        amplitude * (1 - 1 / (2 * visible_count)),
        padding=0,
    )
