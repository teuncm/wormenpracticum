import re

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QWidget

from app.feature.analysis.display_selection import parse_display_selection
from app.feature.analysis.io_recording import StimulusResponse, split_stimulus_responses
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_yolo_window import Ui_AnalyzeYoloWindow


class AnalyzeYoloView(QWidget):
    """Display every pin with a user-controlled total vertical voltage span."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeYoloWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)
        frame, self.plot_widget = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.ui.rightLayout.addWidget(frame)
        # Keep the helper's disabled mouse navigation; clicks still set region bounds.
        self.plot_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.plot_widget.installEventFilter(self)
        self.plot_widget.scene().installEventFilter(self)
        self.plot_widget.getAxis("left").enableAutoSIPrefix(False)
        self.peak_markers = pg.ScatterPlotItem(
            size=11,
            symbol="o",
            hoverable=True,
            hoverSize=15,
            hoverPen=pg.mkPen("k", width=2),
            tip=self._peak_tooltip,
        )
        self.peak_markers.setZValue(10)
        self.plot_widget.addItem(self.peak_markers)
        self.curves = []
        self.pin_labels = []
        self.guide_lines = {"start": [], "lower": [], "upper": []}
        self._data = None
        self._channels = []
        self._metadata = {}
        self._responses = []
        self._pin_responses = []
        self._marker_error = ""
        self._amplitude_initialized = False
        self._physical_pins = {}
        self._displayed_pins = []
        self._displayed_stimuli = []
        self._valid_pin_text = ""
        self._valid_stimulus_text = ""
        self._pin_selector_error = ""
        self._stimulus_selector_error = ""
        self._detection_region_ms: tuple[float | None, float | None] = (None, None)
        self.ui.amplitudeSpinBox.valueChanged.connect(
            lambda _value: self.plot_recording(preserve_x=True)
        )
        self.ui.pinsLineEdit.editingFinished.connect(self._apply_pin_selection)
        self.ui.stimuliLineEdit.editingFinished.connect(self._apply_stimulus_selection)
        self.ui.detectionStartLineEdit.editingFinished.connect(
            self._apply_detection_region
        )
        self.ui.detectionEndLineEdit.editingFinished.connect(
            self._apply_detection_region
        )
        self.ui.minCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.maxCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.showDetectionStartCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showDetectionEndCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showStimulusStartsCheckBox.toggled.connect(self.update_guide_lines)
        self.plot_widget.getPlotItem().getViewBox().setMenuEnabled(False)
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.plot_widget.scene().sigMouseClicked.connect(self._set_region_from_click)
        self.set_data(None)

    def eventFilter(self, watched, event) -> bool:
        """Block plot keyboard navigation without affecting the input controls."""
        if (
            watched in (self.plot_widget, self.plot_widget.scene())
            and event.type() == QEvent.Type.KeyPress
        ):
            return True
        return super().eventFilter(watched, event)

    def set_data(
        self,
        data: pd.DataFrame | None,
        metadata: dict | None = None,
        config: dict | None = None,
    ) -> None:
        """Replace the current recording and use its saved boundaries for detection."""
        self._data = data
        self._metadata = metadata or {}
        self._channels = []
        self._responses = []
        self._physical_pins = {}
        self._marker_error = ""
        if data is not None and not data.empty and "t_(s)" in data:
            mapping = self._metadata.get("pin_channels", {})
            if not isinstance(mapping, dict):
                mapping = {}
            self._channels = [column for column in data if column != "t_(s)"]
            column_order = {
                column: rank + 1 for rank, column in enumerate(self._channels)
            }
            self._physical_pins = {
                column: self._physical_pin(
                    mapping.get(column), column, column_order[column]
                )
                for column in self._channels
            }
            self._channels.sort(key=lambda column: self._physical_pins[column])
            if self._channels:
                try:
                    self._responses = split_stimulus_responses(
                        data, self._channels[0], self._metadata, config or {}
                    )
                except (ValueError, TypeError, KeyError) as exc:
                    self._marker_error = f"Min/max detection unavailable: {exc}"
                if not self._amplitude_initialized:
                    values = data[self._channels].to_numpy(dtype=float)
                    finite = values[np.isfinite(values)]
                    span = float(np.ptp(finite)) if finite.size else 0.0
                    amplitude = max(0.001, span * 1.2) * len(self._channels)
                    with Blocker(self.ui.amplitudeSpinBox):
                        self.ui.amplitudeSpinBox.setValue(amplitude)
                    self._amplitude_initialized = True
        self._refresh_selections()
        self.plot_recording()

    @staticmethod
    def _physical_pin(value: object, column: str, fallback_order: int) -> int:
        """Resolve a positive physical pin ID, falling back to stable AI IDs."""
        try:
            numeric = float(value)
            if np.isfinite(numeric) and numeric >= 1 and numeric.is_integer():
                return int(numeric)
        except (TypeError, ValueError):
            pass
        match = re.fullmatch(r"ai(\d+)(?:_.*)?", column)
        return int(match.group(1)) + 1 if match else fallback_order

    def _refresh_selections(self) -> None:
        """Intersect previous valid selectors with IDs in the new recording."""
        pin_ids = sorted(set(self._physical_pins.values()))
        self._displayed_pins = parse_display_selection(
            self._valid_pin_text, pin_ids, strict=False
        )
        stimulus_ids = [response.number for response in self._responses]
        self._displayed_stimuli = parse_display_selection(
            self._valid_stimulus_text, stimulus_ids, strict=False
        )
        self.ui.pinsLineEdit.setEnabled(bool(pin_ids))
        self.ui.stimuliLineEdit.setEnabled(bool(self._responses))
        self._show_selector_errors()

    def _show_selector_errors(self) -> None:
        """Show any pending selector errors without clearing the other field."""
        message = " ".join(
            error
            for error in (self._pin_selector_error, self._stimulus_selector_error)
            if error
        )
        self.ui.selectionErrorLabel.setText(message)

    def _apply_detection_region(self) -> None:
        """Validate optional inclusive local-time bounds and update markers only."""
        try:
            lower = self._parse_region_bound(self.ui.detectionStartLineEdit.text())
            upper = self._parse_region_bound(self.ui.detectionEndLineEdit.text())
            if lower is not None and upper is not None and lower > upper:
                raise ValueError("Detection start must not exceed detection end.")
        except ValueError as exc:
            self.ui.regionErrorLabel.setText(str(exc))
            self.ui.detectionStartLineEdit.setStyleSheet("color: #b00020")
            self.ui.detectionEndLineEdit.setStyleSheet("color: #b00020")
            return
        self._detection_region_ms = (lower, upper)
        self.ui.regionErrorLabel.clear()
        self.ui.detectionStartLineEdit.setStyleSheet("")
        self.ui.detectionEndLineEdit.setStyleSheet("")
        self.update_peak_markers()
        self.update_guide_lines()

    @staticmethod
    def _parse_region_bound(text: str) -> float | None:
        """Parse a blank or finite nonnegative millisecond value."""
        if not text.strip():
            return None
        try:
            bound = float(text.strip())
        except ValueError as exc:
            raise ValueError(
                "Detection bounds must be finite nonnegative milliseconds."
            ) from exc
        if not np.isfinite(bound) or bound < 0:
            raise ValueError(
                "Detection bounds must be finite nonnegative milliseconds."
            )
        return bound

    def _set_region_from_click(self, event) -> None:
        """Set a region bound from a click inside a displayed stimulus trace."""
        if event.button() not in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            return
        view_box = self.plot_widget.getPlotItem().getViewBox()
        scene_position = event.scenePos()
        if not view_box.sceneBoundingRect().contains(scene_position):
            return
        timestamp = float(view_box.mapSceneToView(scene_position).x())
        local_time = self._local_stimulus_time(timestamp)
        if local_time is None:
            return
        text = f"{local_time * 1000:.12g}"
        target = (
            self.ui.detectionStartLineEdit
            if event.button() == Qt.MouseButton.LeftButton
            else self.ui.detectionEndLineEdit
        )
        target.setText(text)
        self._apply_detection_region()

    def _local_stimulus_time(self, timestamp: float) -> float | None:
        """Map an original timestamp to local seconds within a displayed stimulus."""
        size = self._metadata.get("stimulus_size_samples")
        if type(size) is not int or size <= 0:
            return None
        times = self._data["t_(s)"].to_numpy() if self._data is not None else []
        for response in self._responses:
            if response.number not in self._displayed_stimuli:
                continue
            start = (response.number - 1) * size
            end = min(start + len(response.times_s), len(times))
            if start < end and times[start] <= timestamp <= times[end - 1]:
                return timestamp - float(times[start])
        return None

    def _apply_pin_selection(self) -> None:
        """Apply the pin selector only after its full text validates."""
        try:
            chosen = parse_display_selection(
                self.ui.pinsLineEdit.text(), self._physical_pins.values()
            )
        except ValueError as exc:
            self._pin_selector_error = str(exc)
            self._show_selector_errors()
            return
        self._displayed_pins = chosen
        self._valid_pin_text = self.ui.pinsLineEdit.text()
        self._pin_selector_error = ""
        self._show_selector_errors()
        self.plot_recording(preserve_x=True)

    def _apply_stimulus_selection(self) -> None:
        """Apply the stimulus selector only when recorded boundaries exist."""
        try:
            chosen = parse_display_selection(
                self.ui.stimuliLineEdit.text(),
                (response.number for response in self._responses),
            )
        except ValueError as exc:
            self._stimulus_selector_error = str(exc)
            self._show_selector_errors()
            return
        self._displayed_stimuli = chosen
        self._valid_stimulus_text = self.ui.stimuliLineEdit.text()
        self._stimulus_selector_error = ""
        self._show_selector_errors()
        self.plot_recording()

    def _selected_stimulus_trace(
        self, times: np.ndarray, samples: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Join selected stimulus slices with NaN separators to preserve gaps."""
        size = self._metadata.get("stimulus_size_samples")
        if type(size) is not int or size <= 0:
            return times, samples
        time_parts = []
        sample_parts = []
        previous_number = None
        for number in self._displayed_stimuli:
            start = (number - 1) * size
            end = min(start + size, len(times))
            if start >= len(times) or end <= start:
                continue
            if (
                time_parts
                and previous_number is not None
                and number != previous_number + 1
            ):
                time_parts.append(np.array([np.nan]))
                sample_parts.append(np.array([np.nan]))
            time_parts.append(times[start:end])
            sample_parts.append(samples[start:end])
            previous_number = number
        if not time_parts:
            return np.array([np.nan]), np.array([np.nan])
        return np.concatenate(time_parts), np.concatenate(sample_parts)

    def plot_recording(self, preserve_x: bool = False) -> None:
        """Plot selected pins and stimulus segments on the original timeline."""
        previous_x_range = self.plot_widget.viewRange()[0] if preserve_x else None
        self._clear_guide_lines()
        for item in [*self.curves, *self.pin_labels]:
            self.plot_widget.removeItem(item)
        self.curves = []
        self.pin_labels = []
        self._pin_responses = []
        self.peak_markers.clear()
        displayed_channels = [
            column
            for column in self._channels
            if self._physical_pins.get(column) in self._displayed_pins
        ]
        self.ui.amplitudeSpinBox.setEnabled(bool(self._channels))
        self.ui.minCheckBox.setEnabled(bool(self._responses and displayed_channels))
        self.ui.maxCheckBox.setEnabled(bool(self._responses and displayed_channels))
        if not self._channels:
            self.plot_widget.setTitle("No recording available")
            self.ui.recordingStatusLabel.setText(
                "Load a recording to compare responses across all pins."
            )
            return
        times = self._data["t_(s)"].to_numpy()
        displayed_responses = [
            response
            for response in self._responses
            if response.number in self._displayed_stimuli
        ]
        first_time = float(times[0])
        last_time = float(times[-1])
        if displayed_responses:
            first_time = float(displayed_responses[0].times_s[0])
            # Include the whole final stimulus interval, not just its last sample.
            last_time = (
                float(displayed_responses[-1].times_s[-1])
                + 1 / self._metadata["sample_rate_hz"]
            )
        amplitude = self.ui.amplitudeSpinBox.value()
        channel_count = len(displayed_channels)
        if channel_count == 0:
            self.plot_widget.setTitle("No selected pins")
            self.ui.recordingStatusLabel.setText(
                "No selected pins are present in this recording. Choose available pin IDs."
            )
            return
        channel_spacing = amplitude / channel_count
        mapping = self._metadata.get("pin_channels", {})
        if not isinstance(mapping, dict):
            mapping = {}
        for rank, column in enumerate(displayed_channels):
            offset = rank * channel_spacing
            samples = self._data[column].to_numpy()
            if self._responses:
                plot_times, plot_samples = self._selected_stimulus_trace(times, samples)
            else:
                plot_times, plot_samples = times, samples
            self.curves.append(
                self.plot_widget.plot(
                    plot_times,
                    plot_samples + offset,
                    pen=pg.mkPen("k", width=1),
                    connect="finite",
                )
            )
            pin_id = self._physical_pins[column]
            pin = f"Pin {mapping[column]}" if column in mapping else f"Pin {pin_id}"
            label = pg.TextItem(pin, color="k", anchor=(1, 0.5))
            label.setPos(first_time, offset)
            self.plot_widget.addItem(label, ignoreBounds=True)
            self.pin_labels.append(label)
            for template in self._responses:
                if template.number not in self._displayed_stimuli:
                    continue
                size = self._metadata["stimulus_size_samples"]
                start = (template.number - 1) * size
                response = StimulusResponse(
                    template.number,
                    template.times_s,
                    samples[start : start + len(template.samples_v)],
                    template.stimulus_voltage_v,
                )
                self._pin_responses.append((response, pin, offset))
        self.update_peak_markers()
        self.update_guide_lines()
        reference = self.pin_labels[0].toPlainText()
        pin_summary = (
            "all pins"
            if len(displayed_channels) == len(self._channels)
            else f"{len(displayed_channels)} pins"
        )
        stimulus_summary = (
            "complete recording"
            if not self._responses
            else f"stimuli {', '.join(map(str, self._displayed_stimuli)) or 'none matched'}"
        )
        self.plot_widget.setTitle(f"{stimulus_summary.capitalize()} — {pin_summary}")
        status = (
            f"Voltage axis refers to {reference}. Total visible amplitude: {amplitude:g} V; "
            f"each next pin is shifted up by {channel_spacing:g} V. "
            "Min: cyan; Max: orange. Hover for measured voltage and time."
        )
        if self._marker_error:
            status += f" {self._marker_error}"
        self.ui.recordingStatusLabel.setText(status)
        self.plot_widget.autoRange()
        lower = -amplitude / (2 * channel_count)
        upper = amplitude * (1 - 1 / (2 * channel_count))
        self.plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
        self.plot_widget.setYRange(lower, upper, padding=0)
        duration = max(last_time - first_time, 1e-6)
        if previous_x_range is None:
            self.plot_widget.setXRange(
                first_time - duration * 0.1, last_time, padding=0.02
            )
        else:
            self.plot_widget.setXRange(*previous_x_range, padding=0)

    def _clear_guide_lines(self) -> None:
        """Remove reference lines without disturbing traces or plot ranges."""
        for lines in self.guide_lines.values():
            for line in lines:
                self.plot_widget.removeItem(line)
            lines.clear()

    def update_guide_lines(self) -> None:
        """Show stimulus starts and local detection bounds on the recording timeline."""
        self._clear_guide_lines()
        if not self.curves:
            return
        lower_ms, upper_ms = self._detection_region_ms
        settings = (
            ("start", 0.0, self.ui.showStimulusStartsCheckBox.isChecked(), "#888888"),
            (
                "lower",
                lower_ms,
                self.ui.showDetectionStartCheckBox.isChecked(),
                "#1971c2",
            ),
            (
                "upper",
                upper_ms,
                self.ui.showDetectionEndCheckBox.isChecked(),
                "#e67700",
            ),
        )
        rate = self._metadata.get("sample_rate_hz")
        for response in self._responses:
            if response.number not in self._displayed_stimuli:
                continue
            start_s = float(response.times_s[0])
            duration_ms = len(response.times_s) / rate * 1000
            for kind, bound_ms, visible, color in settings:
                # Unset bounds have no line; out-of-stimulus bounds cannot mark a neighbour.
                if not visible or bound_ms is None or bound_ms > duration_ms:
                    continue
                line = pg.InfiniteLine(
                    pos=start_s + bound_ms / 1000,
                    angle=90,
                    movable=False,
                    pen=pg.mkPen(color, width=1, style=Qt.PenStyle.DotLine),
                )
                line.setZValue(-10 if kind == "start" else -5)
                self.plot_widget.addItem(line, ignoreBounds=True)
                self.guide_lines[kind].append(line)

    @staticmethod
    def _peak_tooltip(x: float, y: float, data: dict) -> str:
        """Show stimulus identity and measured values without the display offset."""
        return (
            f"{data['pin']} · Stimulus {data['number']}\n"
            f"Recorded {data['kind']}: {data['voltage_v']:.6g} V\n"
            f"Time in recording: {x:.6g} s"
        )

    def update_peak_markers(self) -> None:
        """Mark selected first extrema per stimulus per pin without resetting zoom."""
        selected = {
            "min": self.ui.minCheckBox.isChecked(),
            "max": self.ui.maxCheckBox.isChecked(),
        }
        markers = []
        for response, pin, offset in self._pin_responses:
            for kind, (time, voltage) in self._regional_extrema(response).items():
                if selected[kind]:
                    markers.append(
                        {
                            "pos": (time, voltage + offset),
                            "brush": pg.mkBrush("cyan" if kind == "min" else "orange"),
                            "pen": pg.mkPen("k"),
                            "data": {
                                "pin": pin,
                                "number": response.number,
                                "kind": "minimum" if kind == "min" else "maximum",
                                "voltage_v": voltage,
                            },
                        }
                    )
        self.peak_markers.setData(markers)

    def _regional_extrema(
        self, response: StimulusResponse
    ) -> dict[str, tuple[float, float]]:
        """Find first finite extrema within the inclusive local-time region."""
        lower_ms, upper_ms = self._detection_region_ms
        local_ms = (response.times_s - response.times_s[0]) * 1000
        mask = np.isfinite(response.samples_v)
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
        selected = {
            "min": indices[np.argmin(samples)],
            "max": indices[np.argmax(samples)],
        }
        return {
            kind: (float(response.times_s[index]), float(response.samples_v[index]))
            for kind, index in selected.items()
        }
