import numpy as np
import pyqtgraph as pg
from app.model.data_io import read_data
from app.view.data_dialog import show_load_dialog
from app.view.view_helpers import (
    create_plot_widget,
    create_title,
    set_global_plot_config,
    spacer,
)
from app.window.ui_main_window import Ui_MainWindow
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
)

AMP_SLIDER_SCALE_FACTOR = 100


class MainView(QMainWindow):
    editImpulseRequested = Signal()
    editProtocolRequested = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        set_global_plot_config()

        self.ui.loadButton.clicked.connect(self.load_data_with_dialog)

        self.ui.ampSlider.setMaximum(2 * AMP_SLIDER_SCALE_FACTOR)
        self.ui.ampSlider.setValue(0)
        self.ui.ampSlider.valueChanged.connect(self.update_plot_amplitude)

        self.ui.editImpulseButton.clicked.connect(self.editImpulseRequested)
        self.ui.editProtocolButton.clicked.connect(self.editProtocolRequested)

        frame, plot = create_plot_widget(
            title="Evoked Response",
            x_label="Time",
            x_units="s",
            y_label="Voltage",
            y_units="V",
        )

        spacer(self.ui.centralwidget.layout())

        self.ui.plotLayout.addWidget(create_title("Evoked response plot"))
        self.ui.plotLayout.addWidget(frame)
        self.ui.optionsLayout.insertWidget(0, create_title("Actions"))
        self.ui.optionsLayout.insertWidget(3, create_title("Plot options"))
        self.plotWidget = plot

        # legend.anchor((1, 0), (1, 0))
        # legend.setBrush(pg.mkBrush(("w")))

        self.plotMagnitude = 1.0

        # loaded_df = read_data("data/test.parquet")
        # self.plot_data(loaded_df)

    def load_data_with_dialog(self):
        filename = show_load_dialog()

        if filename:
            loaded_df = read_data(filename)
            self.plot_data(loaded_df)

    def plot_data(self, df):
        """Plot data from the file system.

        Args:
            df (DataFrame): DataFrame of data to plot
        """
        for i in range(1, df.shape[1]):
            color = pg.intColor(i, hues=df.shape[1] - 1)
            color.setAlpha(100)

            self.plotWidget.plot(
                df.iloc[:, 0],
                df.iloc[:, i],
                name=f"Channel {i}",
                pen=pg.mkPen(color=color, width=1),
            )

        # Adjust x viewbox limits based on dataframe.
        self.plotWidget.getViewBox().setLimits(
            xMin=df.iloc[:, 0].min(), xMax=df.iloc[:, 0].max()
        )

        self.plotMagnitude = np.max(np.abs(df.iloc[:, 1:]))

    def update_plot_amplitude(self, value):
        """Scale plot amplitude based on slider value.

        Args:
            value (int): Slider value
        """
        view_scale_factor = value / float(AMP_SLIDER_SCALE_FACTOR)
        self.plotWidget.getViewBox().setRange(
            yRange=(
                -view_scale_factor * self.plotMagnitude,
                view_scale_factor * self.plotMagnitude,
            )
        )
