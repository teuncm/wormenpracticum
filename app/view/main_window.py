import pyqtgraph as pg
from PySide6.QtWidgets import QMainWindow, QVBoxLayout

import app.model.data_functions as data_functions
from app.ui.ui_main_window import Ui_MainWindow
from app.ui.ui_tool_view import Ui_ToolView


class MainWindow(QMainWindow):
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
        filename = data_functions.show_load_dialog()

        if filename:
            loaded_df = data_functions.load_data(filename)
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

    def open_second(self):
        self.second_window = QMainWindow()
        self.second_ui = Ui_ToolView()
        self.second_ui.setupUi(self.second_window)
        self.second_window.show()
