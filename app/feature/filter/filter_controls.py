from math import floor

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMenu,
    QSizePolicy,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from app.feature.filter.filter_config import FilterConfig
from app.shared.view_helpers import Blocker


class _FilterMenu(QMenu):
    """Open in the analysis sidebar when there is space beside the plot."""

    def showEvent(self, event) -> None:
        super().showEvent(event)
        button = self.parentWidget()
        screen = button.screen().availableGeometry()
        left = button.mapToGlobal(button.rect().topLeft()).x() - self.width() - 6
        if left < screen.left():
            return  # Let Qt place the menu when it cannot fit to the left.

        bottom = button.mapToGlobal(button.rect().bottomLeft()).y()
        top = min(bottom, screen.bottom()) - self.height() + 1
        self.move(left, max(screen.top(), top))


class FilterControls(QWidget):
    """Edit the shared recording filters inline or from a dropdown."""

    settings_changed = Signal()
    auto_update_changed = Signal(bool)
    _cutoff_steps = 300

    def __init__(self, *, dropdown: bool = False):
        super().__init__()

        self.cutoff = QDoubleSpinBox()
        self.cutoff.setRange(0.01, 100_000)
        self.cutoff.setSuffix(" Hz")

        self.cutoff_slider = QSlider(Qt.Orientation.Horizontal)
        self.cutoff_slider.setAccessibleName("Low-pass cutoff")
        self.cutoff_slider.setRange(0, self._cutoff_steps)
        self._slider_limit_hz = 0.0
        self._recording_available = False

        self.low_pass = QCheckBox("Low-pass filter")
        self.suppress_50hz = QCheckBox("Suppress 50 Hz interference")
        self.remove_dc = QCheckBox("Remove DC offset")

        self.auto_update = QCheckBox("Auto update")
        self.auto_update.setChecked(True)
        self.auto_update.setToolTip("Update the plot while dragging the cutoff slider.")
        self.status = QLabel()
        self.status.setWordWrap(True)
        # Status messages can wrap without widening the sidebar or squeezing the plot.
        self.status.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )

        form = QWidget()
        settings = QFormLayout(form)
        settings.setContentsMargins(0, 0, 0, 0)
        settings.addRow(self.low_pass)
        settings.addRow("Low-pass cutoff", self.cutoff)
        settings.addRow(self.cutoff_slider)
        settings.addRow(self.suppress_50hz)
        settings.addRow(self.remove_dc)
        settings.addRow(self.auto_update)
        settings.addRow(self.status)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if dropdown:
            settings.setContentsMargins(8, 8, 8, 8)
            toggle = QToolButton()
            toggle.setText("Filtering")
            toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toggle.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            menu = _FilterMenu(toggle)
            action = QWidgetAction(menu)
            action.setDefaultWidget(form)
            menu.addAction(action)
            toggle.setMenu(menu)
            layout.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            layout.addWidget(form)

        self.auto_update.toggled.connect(self.auto_update_changed.emit)
        self.low_pass.toggled.connect(self._low_pass_toggled)
        self.cutoff_slider.valueChanged.connect(self._cutoff_dragged)
        self.cutoff.valueChanged.connect(self._cutoff_changed)
        self.suppress_50hz.toggled.connect(
            lambda _checked: self.settings_changed.emit()
        )
        self.remove_dc.toggled.connect(lambda _checked: self.settings_changed.emit())

    def set_config(self, config: FilterConfig, *, inactive_cutoff: float = 0.0) -> None:
        # Loading saved settings must not schedule a new filter pass.
        with Blocker(self.low_pass, self.cutoff, self.suppress_50hz, self.remove_dc):
            self.low_pass.setChecked(bool(config.low_pass_cutoff_hz))
            self.cutoff.setValue(config.low_pass_cutoff_hz or inactive_cutoff)
            self.suppress_50hz.setChecked(config.suppress_50hz)
            self.remove_dc.setChecked(config.remove_dc_offset)

        self._update_cutoff_availability()
        self._sync_cutoff_slider()

    def set_sample_rate(self, rate: float | None) -> None:
        # Round down so the rightmost position stays below Nyquist.
        maximum = min(self.cutoff.maximum(), rate * 0.499) if rate else 0.0
        self._slider_limit_hz = floor(maximum * 100) / 100
        self._update_cutoff_availability()
        self._sync_cutoff_slider()

    def set_auto_update(self, enabled: bool) -> None:
        """Choose whether dragging and typing apply continuously or on commit."""
        with Blocker(self.auto_update):
            self.auto_update.setChecked(enabled)
        self.cutoff_slider.setTracking(enabled)
        self.cutoff.setKeyboardTracking(enabled)

    def set_recording_available(
        self, available: bool, sample_rate: float | None
    ) -> None:
        """Enable editing when there are voltage channels to filter."""
        self._recording_available = available
        self.set_sample_rate(sample_rate if available else None)
        for control in (
            self.low_pass,
            self.suppress_50hz,
            self.remove_dc,
        ):
            control.setEnabled(available)
        self.show_status(
            "" if available else "Record or load data with voltage channels."
        )

    def show_status(self, message: str) -> None:
        self.status.setText(message)
        self.status.setVisible(bool(message))

    def _update_cutoff_availability(self) -> None:
        enabled = self._recording_available and self.low_pass.isChecked()
        self.cutoff.setEnabled(enabled)
        self.cutoff_slider.setEnabled(
            enabled and self._slider_limit_hz > self.cutoff.minimum()
        )

    def _low_pass_toggled(self, enabled: bool) -> None:
        if (
            enabled
            and self.cutoff.minimum() <= self._slider_limit_hz < self.cutoff.value()
        ):
            # A remembered cutoff may be outside the range of a new recording.
            with Blocker(self.cutoff):
                self.cutoff.setValue(self._slider_limit_hz)
            self._sync_cutoff_slider()

        self._update_cutoff_availability()
        self.settings_changed.emit()

    def _cutoff_dragged(self, position: int) -> None:
        minimum = self.cutoff.minimum()
        if self._slider_limit_hz <= minimum:
            return
        # Bypassing the filter is handled by the checkbox, even at the left edge.
        cutoff = (
            minimum + (self._slider_limit_hz - minimum) * position / self._cutoff_steps
        )

        # The spin box rounds the cutoff; don't snap the pointer back to that rounded value.
        with Blocker(self.cutoff_slider):
            self.cutoff.setValue(cutoff)

    def _cutoff_changed(self, _value: float) -> None:
        if not self.cutoff_slider.signalsBlocked():
            self._sync_cutoff_slider()
        self.settings_changed.emit()

    def _sync_cutoff_slider(self) -> None:
        minimum = self.cutoff.minimum()
        position = 0
        if self._slider_limit_hz > minimum:
            fraction = (self.cutoff.value() - minimum) / (
                self._slider_limit_hz - minimum
            )
            position = round(self._cutoff_steps * min(1.0, fraction))

        with Blocker(self.cutoff_slider):
            self.cutoff_slider.setValue(position)

    def to_config(self) -> FilterConfig:
        return FilterConfig(
            self.cutoff.value() if self.low_pass.isChecked() else 0.0,
            self.suppress_50hz.isChecked(),
            self.remove_dc.isChecked(),
        )
