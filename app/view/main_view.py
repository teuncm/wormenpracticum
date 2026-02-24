import pyqtgraph as pg
from app.model.data_io import load_data
from app.view.data_dialog import show_load_dialog
from app.window.ui_main_window import Ui_MainWindow
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
)


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.loadButton.clicked.connect(self.load_data)

        self.plotWidget = pg.PlotWidget()
        layout = QVBoxLayout(self.ui.plotContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotWidget)

        self.plotWidget.setTitle("Evoked Response")
        self.plotWidget.setLabel("left", "Voltage", units="V")
        self.plotWidget.setLabel("bottom", "Time", units="s")
        self.plotWidget.setMouseEnabled(False, False)
        self.plotWidget.setMenuEnabled(False)

    def load_data(self):
        filename = show_load_dialog()

        if filename:
            loaded_df = load_data(filename)
            print(loaded_df)

            for i in range(1, loaded_df.shape[1]):
                color = pg.intColor(i, hues=loaded_df.shape[1] - 1)
                color.setAlpha(100)

                self.plotWidget.plot(
                    loaded_df.iloc[:, 0],
                    loaded_df.iloc[:, i],
                    name=f"Channel {i}",
                    pen=pg.mkPen(color=color, width=1),
                )
