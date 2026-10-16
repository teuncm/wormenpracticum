"""Shared peak-detection region validation, extrema, and plot guides."""

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QLabel, QLineEdit

from app.feature.analysis.io_recording import StimulusResponse


def parse_region_bound(text: str) -> float | None:
    """Parse a blank or finite, nonnegative millisecond bound."""
    if not text.strip():
        return None
    try:
        value = float(text.strip())
    except ValueError as exc:
        raise ValueError(
            "Detection bounds must be finite nonnegative milliseconds."
        ) from exc
    if not np.isfinite(value) or value < 0:
        raise ValueError("Detection bounds must be finite nonnegative milliseconds.")
    return value


class DetectionRegionEditor(QObject):
    """Own and validate the two shared detection-bound text fields."""

    changed = Signal()

    def __init__(
        self, start_edit: QLineEdit, end_edit: QLineEdit, error_label: QLabel
    ) -> None:
        super().__init__(start_edit)
        self.start_edit = start_edit
        self.end_edit = end_edit
        self.error_label = error_label
        self._bounds_ms: tuple[float | None, float | None] = (None, None)
        start_edit.editingFinished.connect(self.apply)
        end_edit.editingFinished.connect(self.apply)

    @property
    def bounds_ms(self) -> tuple[float | None, float | None]:
        """Return the last valid inclusive lower and upper bounds."""
        return self._bounds_ms

    def apply(self) -> bool:
        """Validate both fields, retaining the last valid bounds on errors."""
        try:
            lower = parse_region_bound(self.start_edit.text())
            upper = parse_region_bound(self.end_edit.text())
            if lower is not None and upper is not None and lower > upper:
                raise ValueError("Detection start must not exceed detection end.")
        except ValueError as exc:
            self.error_label.setText(str(exc))
            self.start_edit.setStyleSheet("color: #b00020")
            self.end_edit.setStyleSheet("color: #b00020")
            return False
        self._bounds_ms = (lower, upper)
        self.error_label.clear()
        self.start_edit.setStyleSheet("")
        self.end_edit.setStyleSheet("")
        self.changed.emit()
        return True

    def set_bound_ms(self, side: str, value_ms: float) -> bool:
        """Set one bound from a plot click using round-trip sample precision."""
        if side == "start":
            edit = self.start_edit
        elif side == "end":
            edit = self.end_edit
        else:
            raise ValueError("Bound side must be 'start' or 'end'.")
        edit.setText(f"{value_ms:.12g}")
        return self.apply()


def bounded_extrema(
    response: StimulusResponse,
    bounds_ms: tuple[float | None, float | None],
) -> dict[str, tuple[float, float]]:
    """Find first finite extrema within inclusive local stimulus-time bounds."""
    if not response.times_s.size:
        return {}
    lower_ms, upper_ms = bounds_ms
    local_ms = (response.times_s - response.times_s[0]) * 1000
    mask = np.isfinite(response.samples_v) & np.isfinite(local_ms)
    if lower_ms is not None:
        mask &= (local_ms >= lower_ms) | np.isclose(
            local_ms, lower_ms, rtol=0, atol=1e-6
        )
    if upper_ms is not None:
        mask &= (local_ms <= upper_ms) | np.isclose(
            local_ms, upper_ms, rtol=0, atol=1e-6
        )
    indices = np.flatnonzero(mask)
    if not indices.size:
        return {}
    samples = response.samples_v[indices]
    extrema_indices = {
        "min": indices[np.argmin(samples)],
        "max": indices[np.argmax(samples)],
    }
    return {
        kind: (float(response.times_s[index]), float(response.samples_v[index]))
        for kind, index in extrema_indices.items()
    }


def clear_region_guides(
    plot_widget: pg.PlotWidget, guides: dict[str, list[pg.InfiniteLine]]
) -> None:
    """Remove guide lines while preserving each list for legacy references."""
    for lines in guides.values():
        for line in lines:
            plot_widget.removeItem(line)
        lines.clear()


def draw_region_guides(
    plot_widget: pg.PlotWidget,
    guides: dict[str, list[pg.InfiniteLine]],
    responses: list[StimulusResponse],
    bounds_ms: tuple[float | None, float | None],
    *,
    show_start: bool,
    show_lower: bool,
    show_upper: bool,
    sample_rate_hz: float,
    local_timeline: bool = False,
) -> None:
    """Draw stimulus starts and region bounds on the supplied stimulus set."""
    clear_region_guides(plot_widget, guides)
    lower_ms, upper_ms = bounds_ms
    settings = (
        ("start", 0.0, show_start, "#888888"),
        ("lower", lower_ms, show_lower, "#1971c2"),
        ("upper", upper_ms, show_upper, "#e67700"),
    )
    for response in responses:
        if not response.times_s.size:
            continue
        time_start = 0.0 if local_timeline else float(response.times_s[0])
        duration_ms = len(response.times_s) / sample_rate_hz * 1000
        for kind, bound_ms, visible, color in settings:
            if not visible or bound_ms is None or bound_ms > duration_ms:
                continue
            position = time_start + bound_ms / 1000
            line = pg.InfiniteLine(
                pos=position,
                angle=90,
                movable=False,
                pen=pg.mkPen(color, width=1, style=Qt.PenStyle.DotLine),
            )
            line.setZValue(-10 if kind == "start" else -5)
            plot_widget.addItem(line, ignoreBounds=True)
            guides[kind].append(line)
