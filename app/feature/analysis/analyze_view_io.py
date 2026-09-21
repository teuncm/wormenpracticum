import pandas as pd
from PySide6.QtWidgets import QWidget

from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.analyze_io_window import Ui_AnalyzeIOWindow


class AnalyzeIOView(QWidget):
    """Display one channel of the filtered IO recording at a time."""

    def __init__(self):
        """Initialize the IO controls and the received-stimulus plot."""
        super().__init__()

        self.ui = Ui_AnalyzeIOWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        frame, self.plot_widget = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.ui.rightLayout.addWidget(frame)
        self.curve = self.plot_widget.plot(pen="b", connect="finite")
        self._data: pd.DataFrame | None = None
        self._channels: list[str] = []
        self.ui.channelSlider.valueChanged.connect(self.plot_channel)
        self.set_data(None)

    def set_data(self, data: pd.DataFrame | None) -> None:
        """Show the complete filtered recording, preserving the selected channel."""
        index = self.ui.channelSlider.value() - 1
        selected = self._channels[index] if self._channels else None
        self._data = data
        self._channels = (
            [column for column in data.columns if column != "t_(s)"]
            if data is not None and not data.empty and "t_(s)" in data.columns
            else []
        )
        # Keep the same column selected when a filter refreshes the recording.
        with Blocker(self.ui.channelSlider):
            self.ui.channelSlider.setRange(1, max(1, len(self._channels)))
            self.ui.channelSlider.setValue(
                self._channels.index(selected) + 1 if selected in self._channels else 1
            )
            self.ui.channelSlider.setEnabled(len(self._channels) > 1)
        self.plot_channel()

    def plot_channel(self) -> None:
        """Plot every received sample for the channel selected by the slider."""
        if self._data is None or not self._channels:
            self.curve.clear()
            self.ui.channelLabel.setText("Channel: no data")
            self.plot_widget.setTitle("No filtered recording available")
            return

        index = self.ui.channelSlider.value() - 1
        column = self._channels[index]
        self.ui.channelLabel.setText(f"Channel {index + 1:02d}: {column}")
        self.plot_widget.setTitle("Filtered recording")
        # Acquisition already stores all stimuli consecutively on one time axis.
        self.curve.setData(
            self._data["t_(s)"].to_numpy(), self._data[column].to_numpy()
        )
        self.plot_widget.autoRange()
