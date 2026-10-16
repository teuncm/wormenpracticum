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
from app.ui.generated.analyze_speed_window import Ui_AnalyzeSpeedWindow


class AnalyzeSpeedView(QWidget):
    """Compare one stimulus across physical pins with a shared voltage scale."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeSpeedWindow()
        self.ui.setupUi(self)
        self._region_editor = DetectionRegionEditor(
            self.ui.detectionStartLineEdit,
            self.ui.detectionEndLineEdit,
            self.ui.regionErrorLabel,
        )

        setup_ui_custom(self)
        frame, self.plot_widget = create_plot_widget(
            x_label="Time within stimulus",
            x_units="s",
            y_label="Voltage",
            y_units="V",
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
        self.guide_lines = {"start": [], "lower": [], "upper": []}
        self._detection_region_ms: tuple[float | None, float | None] = (None, None)
        self._amplitude_initialized = False
        self.ui.stimulusComboBox.currentIndexChanged.connect(self._stimulus_changed)
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
        """Use saved stimulus boundaries and retain selection on filter refreshes."""
        previous_index = max(0, self.ui.stimulusComboBox.currentIndex())
        self._data = data
        self._metadata = metadata or {}
        self._channels = []
        self._responses = []
        error = "Load a recording with stimulus metadata."
        if data is not None and not data.empty and "t_(s)" in data:
            mapping = self._metadata.get("pin_channels", {})
            self._channels = [column for column in data if column != "t_(s)"]
            # Physical pin order takes precedence over the order of CSV columns.
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
                    error = f"Cannot select stimuli: {exc}"
        with Blocker(self.ui.stimulusComboBox, self.ui.amplitudeSpinBox):
            self.ui.stimulusComboBox.clear()
            for response in self._responses:
                label = f"Stimulus {response.number}"
                if response.stimulus_voltage_v is not None:
                    label += f" · {response.stimulus_voltage_v:g} V"
                self.ui.stimulusComboBox.addItem(label)
            if self._responses:
                self.ui.stimulusComboBox.setCurrentIndex(
                    min(previous_index, len(self._responses) - 1)
                )
                if not self._amplitude_initialized:
                    values = data[self._channels].to_numpy(dtype=float)
                    self.ui.amplitudeSpinBox.setValue(
                        default_total_amplitude(values, len(self._channels))
                    )
                    self._amplitude_initialized = True
            self.ui.stimulusComboBox.setEnabled(bool(self._responses))
            self.ui.amplitudeSpinBox.setEnabled(bool(self._channels))
        self.ui.recordingStatusLabel.setText(error)
        self.plot_stimulus()

    def _stimulus_changed(self, *_args) -> None:
        """Redraw when the selected stimulus changes."""
        self.plot_stimulus()

    def _amplitude_changed(self, *_args) -> None:
        """Redraw with new vertical spacing while preserving the time zoom."""
        self.plot_stimulus(preserve_x=True)

    def plot_stimulus(self, preserve_x: bool = False) -> None:
        """Slice one stimulus from every pin and apply a constant display offset."""
        previous_x_range = self.plot_widget.viewRange()[0] if preserve_x else None
        for item in [*self.curves, *self.pin_labels]:
            self.plot_widget.removeItem(item)
        self.curves = []
        self.pin_labels = []
        self._pin_responses = []
        self.peak_markers.clear()
        self.vertical_zoom.setEnabled(bool(self._responses))
        self.ui.minCheckBox.setEnabled(bool(self._responses))
        self.ui.maxCheckBox.setEnabled(bool(self._responses))
        if not self._responses:
            clear_region_guides(self.plot_widget, self.guide_lines)
            self.plot_widget.setTitle("No stimulus available")
            self.plot_widget.getAxis("left").setTicks(None)
            return
        index = self.ui.stimulusComboBox.currentIndex()
        size = self._metadata["stimulus_size_samples"]
        segment = self._data.iloc[index * size : (index + 1) * size]
        times = segment["t_(s)"].to_numpy()
        times = times - times[0]
        amplitude = self.vertical_zoom.visible_amplitude(
            self.ui.amplitudeSpinBox.value()
        )
        spacing, offsets = vertical_pin_layout(amplitude, len(self._channels))
        mapping = self._metadata.get("pin_channels", {})
        for rank, column in enumerate(self._channels):
            offset = offsets[rank]
            self.curves.append(
                self.plot_widget.plot(
                    times,
                    segment[column].to_numpy() + offset,
                    pen=pg.mkPen("k", width=1),
                    connect="finite",
                )
            )
            label = pg.TextItem(
                f"Pin {mapping[column]}" if column in mapping else column,
                color="k",
                anchor=(1, 0.5),
            )
            label.setPos(0, offset)
            self.plot_widget.addItem(label, ignoreBounds=True)
            self.pin_labels.append(label)
            response = StimulusResponse(
                index + 1,
                times,
                segment[column].to_numpy(),
                self._responses[index].stimulus_voltage_v,
            )
            self._pin_responses.append((response, label.toPlainText(), offset))
        self.update_peak_markers()
        self.update_guide_lines()
        first = self._channels[0]
        reference = f"Pin {mapping[first]}" if first in mapping else first
        self.plot_widget.setTitle(f"Stimulus {index + 1} — all pins")
        self.ui.recordingStatusLabel.setText(
            f"Voltage axis refers to {reference}. Total visible amplitude: {amplitude:g} V; "
            f"each next pin is shifted up by {spacing:g} V. "
            "Min: cyan; Max: orange. Hover for voltage and time."
        )
        self.plot_widget.autoRange()
        apply_vertical_range(self.plot_widget, amplitude, len(self._channels))
        duration = max(float(times[-1]), 1 / self._metadata["sample_rate_hz"])
        if previous_x_range is None:
            self.plot_widget.setXRange(-duration * 0.1, duration, padding=0.02)
        else:
            self.plot_widget.setXRange(*previous_x_range, padding=0)

    @staticmethod
    def _peak_tooltip(x: float, y: float, data: dict) -> str:
        """Show measured voltage without the display offset and local response time."""
        return (
            f"{data['pin']} · Stimulus {data['number']}\n"
            f"Recorded {data['kind']}: {data['voltage_v']:.6g} V\n"
            f"Time within stimulus: {x:.6g} s"
        )

    def update_peak_markers(self) -> None:
        """Mark selected first extrema for every pin without resetting plot zoom."""
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
        """Validate the local x coordinate within the currently displayed stimulus."""
        if not self._responses or self.ui.stimulusComboBox.currentIndex() < 0:
            return None
        response = self._responses[self.ui.stimulusComboBox.currentIndex()]
        duration = float(response.times_s[-1] - response.times_s[0])
        if 0 <= timestamp <= duration:
            return timestamp
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
        local_time = self._local_stimulus_time(
            float(view_box.mapSceneToView(scene_position).x())
        )
        if local_time is None:
            return
        side = "start" if event.button() == Qt.MouseButton.LeftButton else "end"
        self._region_editor.set_bound_ms(side, local_time * 1000)

    def update_guide_lines(self) -> None:
        """Draw guides for the currently selected stimulus on its local timeline."""
        index = self.ui.stimulusComboBox.currentIndex()
        rate = self._metadata.get("sample_rate_hz")
        if (
            not self.curves
            or not self._responses
            or index < 0
            or not isinstance(rate, (int, float))
            or rate <= 0
        ):
            clear_region_guides(self.plot_widget, self.guide_lines)
            return
        draw_region_guides(
            self.plot_widget,
            self.guide_lines,
            [self._responses[index]],
            self._detection_region_ms,
            show_start=self.ui.showStimulusStartsCheckBox.isChecked(),
            show_lower=self.ui.showDetectionStartCheckBox.isChecked(),
            show_upper=self.ui.showDetectionEndCheckBox.isChecked(),
            sample_rate_hz=rate,
            local_timeline=True,
        )
