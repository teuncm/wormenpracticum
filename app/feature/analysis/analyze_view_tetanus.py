import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

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
from app.ui.generated.analyze_tetanus_window import Ui_AnalyzeTetanusWindow


class AnalyzeTetanusView(QWidget):
    """Display one complete recording across every pin for manual comparison."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeTetanusWindow()
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
        self.plot_widget.setMouseEnabled(x=True, y=True)
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
        self._data = None
        self._channels = []
        self._metadata = {}
        self._responses = []
        self._pin_responses = []
        self._marker_error = ""
        self._amplitude_initialized = False
        self.guide_lines = {"start": [], "lower": [], "upper": []}
        self._detection_region_ms: tuple[float | None, float | None] = (None, None)
        self.ui.amplitudeSpinBox.valueChanged.connect(self._amplitude_changed)
        self.vertical_zoom.zoomChanged.connect(self._amplitude_changed)
        self.ui.minCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.maxCheckBox.toggled.connect(self.update_peak_markers)
        self._region_editor.changed.connect(self._detection_region_changed)
        self.ui.showStimulusStartsCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showDetectionStartCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showDetectionEndCheckBox.toggled.connect(self.update_guide_lines)
        self.plot_widget.getPlotItem().getViewBox().setMenuEnabled(False)
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.plot_widget.scene().sigMouseClicked.connect(self._set_region_from_click)
        self.set_data(None)

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
        self._marker_error = ""
        if data is not None and not data.empty and "t_(s)" in data:
            mapping = self._metadata.get("pin_channels", {})
            self._channels = [column for column in data if column != "t_(s)"]
            column_order = {
                column: rank + 1 for rank, column in enumerate(self._channels)
            }
            self._channels.sort(
                key=lambda column: mapping.get(column, column_order[column])
            )
            if self._channels:
                try:
                    self._responses = split_stimulus_responses(
                        data, self._channels[0], self._metadata, config or {}
                    )
                except (ValueError, TypeError, KeyError) as exc:
                    self._marker_error = f"Min/max detection unavailable: {exc}"
                if not self._amplitude_initialized:
                    values = data[self._channels].to_numpy(dtype=float)
                    with Blocker(self.ui.amplitudeSpinBox):
                        self.ui.amplitudeSpinBox.setValue(
                            default_total_amplitude(values, len(self._channels))
                        )
                    self._amplitude_initialized = True
        self.plot_recording()

    def _amplitude_changed(self, *_args) -> None:
        """Redraw with new vertical spacing while preserving the time zoom."""
        self.plot_recording(preserve_x=True)

    def plot_recording(self, preserve_x: bool = False) -> None:
        """Read each complete pin column directly and add a display-only offset."""
        previous_x_range = self.plot_widget.viewRange()[0] if preserve_x else None
        for item in [*self.curves, *self.pin_labels]:
            self.plot_widget.removeItem(item)
        self.curves = []
        self.pin_labels = []
        self._pin_responses = []
        self.peak_markers.clear()
        clear_region_guides(self.plot_widget, self.guide_lines)
        self.vertical_zoom.setEnabled(bool(self._channels))
        self.ui.amplitudeSpinBox.setEnabled(bool(self._channels))
        self.ui.minCheckBox.setEnabled(bool(self._responses))
        self.ui.maxCheckBox.setEnabled(bool(self._responses))
        if not self._channels:
            self.plot_widget.setTitle("No recording available")
            self.ui.recordingStatusLabel.setText(
                "Load a recording to compare responses across all pins."
            )
            return
        times = self._data["t_(s)"].to_numpy()
        amplitude = self.vertical_zoom.visible_amplitude(
            self.ui.amplitudeSpinBox.value()
        )
        spacing, offsets = vertical_pin_layout(amplitude, len(self._channels))
        mapping = self._metadata.get("pin_channels", {})
        for rank, column in enumerate(self._channels):
            offset = offsets[rank]
            samples = self._data[column].to_numpy()
            self.curves.append(
                self.plot_widget.plot(
                    times,
                    samples + offset,
                    pen=pg.mkPen("k", width=1),
                    connect="finite",
                )
            )
            pin = f"Pin {mapping[column]}" if column in mapping else column
            label = pg.TextItem(pin, color="k", anchor=(1, 0.5))
            label.setPos(float(times[0]), offset)
            self.plot_widget.addItem(label, ignoreBounds=True)
            self.pin_labels.append(label)
            # Segment only for detection; the plotted line remains the entire CSV column.
            for step, template in enumerate(self._responses):
                size = len(template.samples_v)
                response = StimulusResponse(
                    template.number,
                    template.times_s,
                    samples[step * size : (step + 1) * size],
                    template.stimulus_voltage_v,
                )
                self._pin_responses.append((response, pin, offset))
        self.update_peak_markers()
        self.update_guide_lines()
        reference = self.pin_labels[0].toPlainText()
        self.plot_widget.setTitle("Complete recording — all pins")
        status = (
            f"Voltage axis refers to {reference}. Total visible amplitude: {amplitude:g} V; "
            f"each next pin is shifted up by {spacing:g} V. "
            "Min: cyan; Max: orange. Hover for measured voltage and time."
        )
        if self._marker_error:
            status += f" {self._marker_error}"
        self.ui.recordingStatusLabel.setText(status)
        self.plot_widget.autoRange()
        apply_vertical_range(self.plot_widget, amplitude, len(self._channels))
        duration = max(float(times[-1] - times[0]), 1e-6)
        if previous_x_range is None:
            self.plot_widget.setXRange(
                float(times[0]) - duration * 0.1, float(times[-1]), padding=0.02
            )
        else:
            self.plot_widget.setXRange(*previous_x_range, padding=0)

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
            for kind, (time, voltage) in bounded_extrema(
                response, self._detection_region_ms
            ).items():
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

    def _apply_detection_region(self) -> None:
        """Validate region edits through the shared editor."""
        self._region_editor.apply()

    def _detection_region_changed(self) -> None:
        """Refresh extrema and guides without changing trace data or zoom."""
        self._detection_region_ms = self._region_editor.bounds_ms
        self.update_peak_markers()
        self.update_guide_lines()

    @staticmethod
    def _parse_region_bound(text: str) -> float | None:
        """Keep the common bound parser available for view-level callers."""
        return parse_region_bound(text)

    def _local_stimulus_time(self, timestamp: float) -> float | None:
        """Map a full recording timestamp to a stimulus-local time."""
        for response in self._responses:
            if response.times_s[0] <= timestamp <= response.times_s[-1]:
                return timestamp - float(response.times_s[0])
        return None

    def _set_region_from_click(self, event) -> None:
        """Use left and right plot clicks to set local lower and upper bounds."""
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

    def update_guide_lines(self) -> None:
        """Draw optional stimulus starts and local-time bounds for all responses."""
        rate = self._metadata.get("sample_rate_hz")
        if (
            not self.curves
            or not self._responses
            or not isinstance(rate, (int, float))
            or rate <= 0
        ):
            clear_region_guides(self.plot_widget, self.guide_lines)
            return
        draw_region_guides(
            self.plot_widget,
            self.guide_lines,
            self._responses,
            self._detection_region_ms,
            show_start=self.ui.showStimulusStartsCheckBox.isChecked(),
            show_lower=self.ui.showDetectionStartCheckBox.isChecked(),
            show_upper=self.ui.showDetectionEndCheckBox.isChecked(),
            sample_rate_hz=rate,
        )
