import re

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QWidget

from app.feature.analysis.display_selection import parse_display_selection
from app.feature.analysis.io_recording import StimulusResponse, split_stimulus_responses
from app.feature.analysis.region_selection import (
    DetectionRegionEditor,
    bounded_extrema,
    clear_region_guides,
    draw_region_guides,
    parse_region_bound,
)
from app.feature.analysis.vertical_scale import (
    add_vertical_zoom,
    apply_vertical_range,
    default_total_amplitude,
    vertical_pin_layout,
)
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_yolo_window import Ui_AnalyzeYoloWindow


class AnalyzeYoloView(QWidget):
    """Display every pin with a user-controlled total vertical voltage span."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeYoloWindow()
        self.ui.setupUi(self)
        self._region_editor = DetectionRegionEditor(
            self.ui.detectionStartLineEdit,
            self.ui.detectionEndLineEdit,
            self.ui.regionErrorLabel,
        )

        setup_ui_custom(self)
        frame, self.plot_widget = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.vertical_zoom = add_vertical_zoom(self.ui.rightLayout, frame)
        # Keep the helper's disabled mouse navigation; clicks still set region bounds.
        self.plot_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.plot_widget.installEventFilter(self)
        self._plot_scene = self.plot_widget.scene()
        self._plot_scene.installEventFilter(self)
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
        self.vertical_zoom.zoomChanged.connect(
            lambda _factor: self.plot_recording(preserve_x=True)
        )
        self.ui.pinsLineEdit.editingFinished.connect(self._apply_pin_selection)
        self.ui.stimuliLineEdit.editingFinished.connect(self._apply_stimulus_selection)
        self._region_editor.changed.connect(self._detection_region_changed)
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
        if event.type() == QEvent.Type.KeyPress and (
            watched is self.plot_widget or watched is self._plot_scene
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
                    amplitude = default_total_amplitude(values, len(self._channels))
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
        self._region_editor.apply()

    def _detection_region_changed(self) -> None:
        """Refresh region state, markers, and lines after valid edits."""
        self._detection_region_ms = self._region_editor.bounds_ms
        self.update_peak_markers()
        self.update_guide_lines()

    @staticmethod
    def _parse_region_bound(text: str) -> float | None:
        """Parse a blank or finite nonnegative millisecond value."""
        return parse_region_bound(text)

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
        side = "start" if event.button() == Qt.MouseButton.LeftButton else "end"
        self._region_editor.set_bound_ms(side, local_time * 1000)

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
        self.vertical_zoom.setEnabled(bool(self._channels))
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
        amplitude = self.vertical_zoom.visible_amplitude(
            self.ui.amplitudeSpinBox.value()
        )
        channel_count = len(displayed_channels)
        if channel_count == 0:
            self.plot_widget.setTitle("No selected pins")
            self.ui.recordingStatusLabel.setText(
                "No selected pins are present in this recording. Choose available pin IDs."
            )
            return
        channel_spacing, offsets = vertical_pin_layout(amplitude, channel_count)
        mapping = self._metadata.get("pin_channels", {})
        if not isinstance(mapping, dict):
            mapping = {}
        for rank, column in enumerate(displayed_channels):
            offset = offsets[rank]
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
        apply_vertical_range(self.plot_widget, amplitude, channel_count)
        duration = max(last_time - first_time, 1e-6)
        if previous_x_range is None:
            self.plot_widget.setXRange(
                first_time - duration * 0.1, last_time, padding=0.02
            )
        else:
            self.plot_widget.setXRange(*previous_x_range, padding=0)

    def _clear_guide_lines(self) -> None:
        """Remove reference lines without disturbing traces or plot ranges."""
        clear_region_guides(self.plot_widget, self.guide_lines)

    def update_guide_lines(self) -> None:
        """Show stimulus starts and local detection bounds on the recording timeline."""
        self._clear_guide_lines()
        if not self.curves or not self._responses:
            return
        responses = [
            response
            for response in self._responses
            if response.number in self._displayed_stimuli
        ]
        draw_region_guides(
            self.plot_widget,
            self.guide_lines,
            responses,
            self._detection_region_ms,
            show_start=self.ui.showStimulusStartsCheckBox.isChecked(),
            show_lower=self.ui.showDetectionStartCheckBox.isChecked(),
            show_upper=self.ui.showDetectionEndCheckBox.isChecked(),
            sample_rate_hz=self._metadata["sample_rate_hz"],
        )

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
        return bounded_extrema(response, self._detection_region_ms)
