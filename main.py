import sys

import pandas as pd
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

# from misc.util import load_ui, resolve
from tools.utility_functions import resolve_project
from ui.ui_main_window import Ui_MainWindow
from ui.ui_tool_view import Ui_ToolView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.open_second)
        self.ui.slider1.valueChanged.connect(self.ui.slider1Label.setNum)

    def open_second(self):
        self.second_window = QMainWindow()
        self.second_ui = Ui_ToolView()
        self.second_ui.setupUi(self.second_window)
        self.second_window.show()


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Set global window icon
    app.setWindowIcon(QIcon(resolve_project("ui/icon.ico")))
    main = MainWindow()
    main.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
