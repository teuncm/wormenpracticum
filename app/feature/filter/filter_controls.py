from math import floor, log

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from app.feature.filter.filter_config import FilterConfig
from app.shared.view_helpers import Blocker


class FilterControls(QWidget):
    """Edit the shared recording filters inline or from a dropdown."""

    apply_requested = Signal()
    settings_changed = Signal()
    _cutoff_steps = 300

    def __init__(self, *, dropdown: bool = False):
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

        self.apply_button = QPushButton("Apply filters")
        self.status = QLabel()
        self.status.setWordWrap(True)
        # Status messages can wrap without widening the sidebar or squeezing the plot.
        self.status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )

        form = QWidget()
        settings = QFormLayout(form)
        settings.setContentsMargins(0, 0, 0, 0)
        settings.addRow("Low-pass cutoff", self.cutoff)
        settings.addRow(self.cutoff_slider)
        settings.addRow(self.suppress_50hz)
        settings.addRow(self.remove_dc)
        settings.addRow(self.apply_button)
        settings.addRow(self.status)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if dropdown:
            settings.setContentsMargins(8, 8, 8, 8)
            toggle = QToolButton()
            toggle.setText("Filtering")
            toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toggle.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            menu = QMenu(toggle)
            action = QWidgetAction(menu)
            action.setDefaultWidget(form)
            menu.addAction(action)
            toggle.setMenu(menu)
            layout.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            layout.addWidget(form)

        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_requested.emit)
        self.cutoff_slider.valueChanged.connect(self._cutoff_dragged)
        self.cutoff.valueChanged.connect(self._cutoff_changed)
        self.suppress_50hz.toggled.connect(
            lambda _checked: self.settings_changed.emit()
        )
        self.remove_dc.toggled.connect(lambda _checked: self.settings_changed.emit())

    def set_config(self, config: FilterConfig) -> None:
        # Loading saved settings must not schedule a new filter pass.
        with Blocker(self.cutoff, self.suppress_50hz, self.remove_dc):
            self.cutoff.setValue(config.low_pass_cutoff_hz)
            self.suppress_50hz.setChecked(config.suppress_50hz)
            self.remove_dc.setChecked(config.remove_dc_offset)

        self._sync_cutoff_slider()

    def set_sample_rate(self, rate: float | None) -> None:
        # Reserve the leftmost position for Off; the rest of the scale is logarithmic.
        maximum = min(self.cutoff.maximum(), rate * 0.499) if rate else 0.0
        self._slider_limit_hz = floor(maximum * 100) / 100
        self.cutoff_slider.setEnabled(self._slider_limit_hz >= 0.01)
        self._sync_cutoff_slider()

    def set_recording_available(
        self, available: bool, sample_rate: float | None
    ) -> None:
        """Enable editing when there are voltage channels to filter."""
        self.set_sample_rate(sample_rate if available else None)
        for control in (
            self.cutoff,
            self.suppress_50hz,
            self.remove_dc,
            self.apply_button,
        ):
            control.setEnabled(available)
        self.status.setText(
            "Adjust the filters to update the signal live."
            if available
            else "Record or load data with voltage channels."
        )

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
