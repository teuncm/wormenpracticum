import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
)

from app.shared.view_helpers import (
    Blocker,
    create_plot_widget,
    setup_ui_custom,
)
from app.feature.filter.filter_config import FilterConfig
from app.ui.generated.overview_window import Ui_OverviewWindow

AMP_SLIDER_SCALE_FACTOR = 100


class OverviewView(QWidget):
    requestDataLoad = Signal()
    requestDataSave = Signal()
    filterChanged = Signal()
    _current_df: pd.DataFrame | None = None

    def __init__(self):
        super().__init__()

        self.ui = Ui_OverviewWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.ui.ampSlider.valueChanged.connect(self.update_plot_amplitude)
        self.ui.doubleSpinBox.setRange(0.0, 100000.0)
        self.ui.doubleSpinBox.setDecimals(2)
        self.ui.doubleSpinBox.valueChanged.connect(self.filterChanged)
        self.ui.suppress50HzCheckBox.toggled.connect(self.filterChanged)
        self.ui.removeDCOffsetCheckBox.toggled.connect(self.filterChanged)

        self.plotMagnitude = 1.0
        self.setup_widgets()

    def update_from_config(self, filter_config: FilterConfig):
        """Update filter controls from a config object."""
        with Blocker(
            self.ui.doubleSpinBox,
            self.ui.suppress50HzCheckBox,
            self.ui.removeDCOffsetCheckBox,
        ):
            self.ui.doubleSpinBox.setValue(filter_config.low_pass_cutoff_hz)
            self.ui.suppress50HzCheckBox.setChecked(filter_config.suppress_50hz)
            self.ui.removeDCOffsetCheckBox.setChecked(
                filter_config.remove_dc_offset
            )

    def to_filter_config(self) -> FilterConfig:
        """Read the filter controls into a config object."""
        return FilterConfig(
            low_pass_cutoff_hz=self.ui.doubleSpinBox.value(),
            suppress_50hz=self.ui.suppress50HzCheckBox.isChecked(),
            remove_dc_offset=self.ui.removeDCOffsetCheckBox.isChecked(),
        )

    def setup_widgets(self):
        """Set up the main plot and controls."""
        self.ui.ampSlider.setMaximum(2 * AMP_SLIDER_SCALE_FACTOR)
        self.ui.ampSlider.setValue(0)
        self.ui.ampSlider.setEnabled(False)

        frame, plot = create_plot_widget()

        self.ui.rightLayout.addWidget(frame)
        self.plotWidget = plot

        # Channel slider for data viewing
        self._current_df = None
        self.channel_slider = self.ui.channelSlider
        self.channel_slider.setMinimum(0)
        self.channel_slider.setValue(0)
        self.channel_slider.setEnabled(False)
        self.channel_slider.valueChanged.connect(self.on_channel_changed)

    def on_load_triggered(self, checked=False):
        self.requestDataLoad.emit()

    def on_save_triggered(self, checked=False):
        self.requestDataSave.emit()

    def plot_data(self, df):
        """Plot data from the file system.

        Args:
            df (DataFrame): DataFrame of data to plot
        """
        self._current_df = df

        # Set up channel slider
        n_channels = df.shape[1] - 1  # Exclude time column
        self.channel_slider.setMaximum(n_channels - 1)
        self.channel_slider.setValue(0)
        self.channel_slider.setEnabled(True)

        # Plot the first channel
        self.plotWidget.clear()
        self.plot_channel(0)

        # Enable amplitude slider now that data is loaded
        self.ui.ampSlider.setEnabled(True)

        # Adjust x viewbox limits based on dataframe.
        self.plotWidget.getViewBox().setLimits(
            xMin=df.iloc[:, 0].min(), xMax=df.iloc[:, 0].max()
        )

        self.plotMagnitude = np.max(np.abs(df.iloc[:, 1:]))

    def plot_channel(self, channel_idx):
        """Plot a single channel from the loaded data.

        Args:
            channel_idx (int): Index of the channel to plot (0-based, excluding time)
        """
        if (
            self._current_df is None
            or channel_idx < 0
            or channel_idx >= self._current_df.shape[1] - 1
        ):
            return

        # Column index is channel_idx + 1 (since column 0 is time)
        col_idx = channel_idx + 1
        channel_name = self._current_df.columns[col_idx]

        self.plotWidget.plot(
            self._current_df.iloc[:, 0],
            self._current_df.iloc[:, col_idx],
            name=channel_name,
            pen=pg.mkPen(color="b", width=2),
        )

    def on_channel_changed(self, value):
        """Handle channel slider changes.

        Args:
            value (int): New channel index
        """
        if self._current_df is not None:
            self.plotWidget.clear()
            self.plot_channel(value)

    def update_plot_amplitude(self, value):
        """Scale plot amplitude based on slider value.

        Args:
            value (int): Slider value
        """
        view_scale_factor = value / float(AMP_SLIDER_SCALE_FACTOR)
        self.plotWidget.getViewBox().setRange(
            yRange=(
                # -view_scale_factor * self.plotMagnitude,
                # view_scale_factor * self.plotMagnitude,
                -view_scale_factor * 2,
                view_scale_factor * 2,
            )
        )
