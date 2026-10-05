import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget

from app.feature.analysis.io_recording import StimulusResponse, split_stimulus_responses
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_tetanus_window import Ui_AnalyzeTetanusWindow


class AnalyzeTetanusView(QWidget):
    """Display one complete recording across every pin for manual comparison."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeTetanusWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)
        frame, self.plot_widget = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.ui.rightLayout.addWidget(frame)
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
        self.ui.offsetSpinBox.valueChanged.connect(self.plot_recording)
        self.ui.minCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.maxCheckBox.toggled.connect(self.update_peak_markers)
        self.set_data(None)

    def set_data(
        self,
        data: pd.DataFrame | None,
        metadata: dict | None = None,
        config: dict | None = None,
    ) -> None:
        """Replace the current recording and use its saved boundaries for detection."""
        initialize_spacing = self._data is None
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
                if initialize_spacing:
                    values = data[self._channels].to_numpy(dtype=float)
                    finite = values[np.isfinite(values)]
                    span = float(np.ptp(finite)) if finite.size else 0.0
                    with Blocker(self.ui.offsetSpinBox):
                        self.ui.offsetSpinBox.setValue(max(0.001, span * 1.2))
        self.plot_recording()

    def plot_recording(self) -> None:
        """Read each complete pin column directly and add a display-only offset."""
        for item in [*self.curves, *self.pin_labels]:
            self.plot_widget.removeItem(item)
        self.curves = []
        self.pin_labels = []
        self._pin_responses = []
        self.peak_markers.clear()
        self.ui.offsetSpinBox.setEnabled(bool(self._channels))
        self.ui.minCheckBox.setEnabled(bool(self._responses))
        self.ui.maxCheckBox.setEnabled(bool(self._responses))
        if not self._channels:
            self.plot_widget.setTitle("No recording available")
            self.ui.recordingStatusLabel.setText(
                "Load a recording to compare responses across all pins."
            )
            return
        times = self._data["t_(s)"].to_numpy()
        spacing = self.ui.offsetSpinBox.value()
        mapping = self._metadata.get("pin_channels", {})
        for rank, column in enumerate(self._channels):
            offset = rank * spacing
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
        reference = self.pin_labels[0].toPlainText()
        self.plot_widget.setTitle("Complete recording — all pins")
        status = (
            f"Voltage axis refers to {reference}. Each next pin is shifted up by {spacing:g} V. "
            "Min: cyan; Max: orange. Hover for measured voltage and time."
        )
        if self._marker_error:
            status += f" {self._marker_error}"
        self.ui.recordingStatusLabel.setText(status)
        self.plot_widget.autoRange()
        duration = max(float(times[-1] - times[0]), 1e-6)
        self.plot_widget.setXRange(
            float(times[0]) - duration * 0.1, float(times[-1]), padding=0.02
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
            for kind, (time, voltage) in response.extrema().items():
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
