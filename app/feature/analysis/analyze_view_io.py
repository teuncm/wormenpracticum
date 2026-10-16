import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QWidget

from app.feature.analysis.io_recording import split_stimulus_responses
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
)
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_io_window import Ui_AnalyzeIOWindow


class AnalyzeIOView(QWidget):
    """Display the concatenated recording as one trace for the selected pin."""

    def __init__(self):
        """Initialize the IO controls and the received-stimulus plot."""
        super().__init__()

        self.ui = Ui_AnalyzeIOWindow()
        self.ui.setupUi(self)
        self._region_editor = DetectionRegionEditor(
            self.ui.detectionStartLineEdit,
            self.ui.detectionEndLineEdit,
            self.ui.regionErrorLabel,
        )

        self.pin_selector = QComboBox(self)
        self.pin_selector.setAccessibleName("Recording pin")
        self.ui.leftLayout.insertWidget(2, self.pin_selector)
        self.ui.channelSlider.hide()
        self.recording_status = QLabel(self)
        self.recording_status.setWordWrap(True)
        self.ui.leftLayout.insertWidget(
            self.ui.leftLayout.count() - 1, self.recording_status
        )

        setup_ui_custom(self)

        frame, self.plot_widget = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.vertical_zoom = add_vertical_zoom(self.ui.rightLayout, frame)
        self.plot_widget.getAxis("left").enableAutoSIPrefix(False)
        self.curve = self.plot_widget.plot(pen=pg.mkPen("k", width=1), connect="finite")
        self.peak_markers = pg.ScatterPlotItem(
            size=11,
            symbol="o",
            hoverable=True,
            hoverSize=15,
            hoverPen=pg.mkPen("k", width=2),
            tip=self._peak_tooltip,
        )
        self.plot_widget.addItem(self.peak_markers)
        self.peak_markers.setZValue(10)
        self.responses = []
        self.guide_lines = {"start": [], "lower": [], "upper": []}
        self.boundary_lines = self.guide_lines["start"]
        self._detection_region_ms: tuple[float | None, float | None] = (None, None)
        self._data: pd.DataFrame | None = None
        self._channels: list[str] = []
        self._metadata = {}
        self._config = {}
        self._amplitude_initialized = False
        self.pin_selector.currentIndexChanged.connect(self._select_pin)
        self.ui.channelSlider.valueChanged.connect(self.plot_channel)
        self.ui.amplitudeSpinBox.valueChanged.connect(self._apply_amplitude_range)
        self.vertical_zoom.zoomChanged.connect(self._apply_amplitude_range)
        self._region_editor.changed.connect(self._detection_region_changed)
        self.ui.showStimulusStartsCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showDetectionStartCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.showDetectionEndCheckBox.toggled.connect(self.update_guide_lines)
        self.ui.minCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.maxCheckBox.toggled.connect(self.update_peak_markers)
        self.plot_widget.getPlotItem().getViewBox().setMenuEnabled(False)
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.plot_widget.scene().sigMouseClicked.connect(self._set_region_from_click)
        self.set_data(None)

    @staticmethod
    def _peak_tooltip(x: float, y: float, data: dict) -> str:
        """Describe the selected extreme and stimulus voltage on hover."""
        voltage = data["stimulus_voltage_v"]
        stimulus = f"{voltage:g} V" if voltage is not None else "unavailable"
        return (
            f"{data['pin']} · Stimulus {data['number']}\n"
            f"Recorded {data['kind']}: {y:.6g} V\n"
            f"Time in recording: {x:.6g} s\n"
            f"Stimulation output peak: {stimulus}"
        )

    def set_data(
        self,
        data: pd.DataFrame | None,
        metadata: dict | None = None,
        config: dict | None = None,
    ) -> None:
        """Update the continuous recording, preserving the selected pin."""
        index = self.ui.channelSlider.value() - 1
        selected = self._channels[index] if self._channels else None
        self._data = data
        self._metadata = metadata or {}
        self._config = config or {}
        self._channels = (
            [column for column in data.columns if column != "t_(s)"]
            if data is not None and not data.empty and "t_(s)" in data.columns
            else []
        )
        # Keep the same column selected when a filter refreshes the recording.
        with Blocker(self.ui.channelSlider, self.pin_selector):
            self.ui.channelSlider.setRange(1, max(1, len(self._channels)))
            self.ui.channelSlider.setValue(
                self._channels.index(selected) + 1 if selected in self._channels else 1
            )
            self.ui.channelSlider.setEnabled(len(self._channels) > 1)
            self.pin_selector.clear()
            for column in self._channels:
                pin = self._metadata.get("pin_channels", {}).get(column)
                self.pin_selector.addItem(f"Pin {pin}: {column}" if pin else column)
            self.pin_selector.setCurrentIndex(self.ui.channelSlider.value() - 1)
            self.pin_selector.setEnabled(bool(self._channels))
            if self._channels and not self._amplitude_initialized:
                amplitude = default_total_amplitude(
                    self._data[self._channels].to_numpy(dtype=float), 1
                )
                with Blocker(self.ui.amplitudeSpinBox):
                    self.ui.amplitudeSpinBox.setValue(amplitude)
                self._amplitude_initialized = True
        self.plot_channel()

    def _select_pin(self, index: int) -> None:
        """Keep pin selection and the channel index synchronized."""
        if index >= 0:
            self.ui.channelSlider.setValue(index + 1)

    def plot_channel(self) -> None:
        """Update the same line with all samples and refresh its peak markers."""
        clear_region_guides(self.plot_widget, self.guide_lines)
        self.responses = []
        self.peak_markers.clear()
        self.recording_status.clear()
        self.ui.minCheckBox.setEnabled(False)
        self.ui.maxCheckBox.setEnabled(False)
        self.vertical_zoom.setEnabled(bool(self._channels))
        self.ui.amplitudeSpinBox.setEnabled(bool(self._channels))
        if self._data is None or not self._channels:
            self.curve.clear()
            self.ui.channelLabel.setText("Channel: no data")
            self.plot_widget.setTitle("No filtered recording available")
            return

        index = self.ui.channelSlider.value() - 1
        column = self._channels[index]
        with Blocker(self.pin_selector):
            self.pin_selector.setCurrentIndex(index)
        pin = self._metadata.get("pin_channels", {}).get(column)
        self.ui.channelLabel.setText(
            f"Pin {pin}: {column}" if pin else f"Channel {index + 1:02d}: {column}"
        )
        self.plot_widget.setTitle(
            f"Complete recording — Pin {pin}"
            if pin
            else f"Complete recording — {column}"
        )
        # All stimuli are already concatenated along the saved recording timeline.
        self.curve.setData(
            self._data["t_(s)"].to_numpy(), self._data[column].to_numpy()
        )
        if self._metadata:
            try:
                self.responses = split_stimulus_responses(
                    self._data, column, self._metadata, self._config
                )
            except (ValueError, TypeError, KeyError) as exc:
                self.recording_status.setText(f"Peak markers unavailable: {exc}")
        else:
            self.recording_status.setText("All recorded samples for the selected pin.")
        if self.responses:
            self.ui.minCheckBox.setEnabled(True)
            self.ui.maxCheckBox.setEnabled(True)
            self.update_peak_markers()
            self.recording_status.setText(
                f"{len(self.responses)} concatenated stimuli. Min: cyan; Max: orange. "
                "Hover over a marker to read its voltage. Tied extremes use their first occurrence."
            )
            if self._metadata.get("device_name") == "SyntheticDAQ":
                self.recording_status.setText(
                    self.recording_status.text() + " Synthetic signals: test recording."
                )
        self.plot_widget.autoRange()
        self.update_guide_lines()
        self._apply_amplitude_range()

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
        for response in self.responses:
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
        if not self.responses or not isinstance(rate, (int, float)) or rate <= 0:
            clear_region_guides(self.plot_widget, self.guide_lines)
            return
        draw_region_guides(
            self.plot_widget,
            self.guide_lines,
            self.responses,
            self._detection_region_ms,
            show_start=self.ui.showStimulusStartsCheckBox.isChecked(),
            show_lower=self.ui.showDetectionStartCheckBox.isChecked(),
            show_upper=self.ui.showDetectionEndCheckBox.isChecked(),
            sample_rate_hz=rate,
        )

    def _apply_amplitude_range(self, *_args) -> None:
        """Apply the selected centered voltage span without shifting raw data."""
        amplitude = self.vertical_zoom.visible_amplitude(
            self.ui.amplitudeSpinBox.value()
        )
        apply_vertical_range(self.plot_widget, amplitude, 1)

    def update_peak_markers(self) -> None:
        """Show the selected extremes without changing the trace or plot zoom."""
        self.peak_markers.clear()
        if not self.responses:
            return
        column = self._channels[self.ui.channelSlider.value() - 1]
        pin = self._metadata.get("pin_channels", {}).get(column)
        selected = {
            "min": self.ui.minCheckBox.isChecked(),
            "max": self.ui.maxCheckBox.isChecked(),
        }
        markers = []
        for response in self.responses:
            for kind, position in bounded_extrema(
                response, self._detection_region_ms
            ).items():
                if selected[kind]:
                    markers.append(
                        {
                            "pos": position,
                            "brush": pg.mkBrush("cyan" if kind == "min" else "orange"),
                            "pen": pg.mkPen("k"),
                            "data": {
                                "kind": "minimum" if kind == "min" else "maximum",
                                "number": response.number,
                                "pin": f"Pin {pin}" if pin else column,
                                "stimulus_voltage_v": response.stimulus_voltage_v,
                            },
                        }
                    )
        self.peak_markers.setData(markers)
