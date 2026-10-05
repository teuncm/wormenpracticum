import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget

from app.feature.analysis.io_recording import StimulusResponse, split_stimulus_responses
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_speed_window import Ui_AnalyzeSpeedWindow


class AnalyzeSpeedView(QWidget):
    """Compare one stimulus across physical pins with a shared voltage scale."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeSpeedWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)
        frame, self.plot_widget = create_plot_widget(
            x_label="Time within stimulus",
            x_units="s",
            y_label="Voltage",
            y_units="V",
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
        self.ui.stimulusComboBox.currentIndexChanged.connect(self.plot_stimulus)
        self.ui.offsetSpinBox.valueChanged.connect(self.plot_stimulus)
        self.ui.minCheckBox.toggled.connect(self.update_peak_markers)
        self.ui.maxCheckBox.toggled.connect(self.update_peak_markers)
        self.set_data(None)

    def set_data(
        self,
        data: pd.DataFrame | None,
        metadata: dict | None = None,
        config: dict | None = None,
    ) -> None:
        """Use saved stimulus boundaries and retain selection on filter refreshes."""
        previous_index = max(0, self.ui.stimulusComboBox.currentIndex())
        initialize_spacing = self._data is None
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
        with Blocker(self.ui.stimulusComboBox, self.ui.offsetSpinBox):
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
                if initialize_spacing:
                    values = data[self._channels].to_numpy(dtype=float)
                    finite = values[np.isfinite(values)]
                    span = float(np.ptp(finite)) if finite.size else 0.0
                    self.ui.offsetSpinBox.setValue(max(0.001, span * 1.2))
            self.ui.stimulusComboBox.setEnabled(bool(self._responses))
            self.ui.offsetSpinBox.setEnabled(bool(self._responses))
        self.ui.recordingStatusLabel.setText(error)
        self.plot_stimulus()

    def plot_stimulus(self) -> None:
        """Slice one stimulus from every pin and apply a constant display offset."""
        for item in [*self.curves, *self.pin_labels]:
            self.plot_widget.removeItem(item)
        self.curves = []
        self.pin_labels = []
        self._pin_responses = []
        self.peak_markers.clear()
        self.ui.minCheckBox.setEnabled(bool(self._responses))
        self.ui.maxCheckBox.setEnabled(bool(self._responses))
        if not self._responses:
            self.plot_widget.setTitle("No stimulus available")
            self.plot_widget.getAxis("left").setTicks(None)
            return
        index = self.ui.stimulusComboBox.currentIndex()
        size = self._metadata["stimulus_size_samples"]
        segment = self._data.iloc[index * size : (index + 1) * size]
        times = segment["t_(s)"].to_numpy()
        times = times - times[0]
        spacing = self.ui.offsetSpinBox.value()
        mapping = self._metadata.get("pin_channels", {})
        for rank, column in enumerate(self._channels):
            offset = rank * spacing
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
        first = self._channels[0]
        reference = f"Pin {mapping[first]}" if first in mapping else first
        self.plot_widget.setTitle(f"Stimulus {index + 1} — all pins")
        self.ui.recordingStatusLabel.setText(
            f"Voltage axis refers to {reference}. Each next pin is shifted up by {spacing:g} V. "
            "Min: cyan; Max: orange. Hover for voltage and time."
        )
        self.plot_widget.autoRange()
        duration = max(float(times[-1]), 1 / self._metadata["sample_rate_hz"])
        self.plot_widget.setXRange(-duration * 0.1, duration, padding=0.02)

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
