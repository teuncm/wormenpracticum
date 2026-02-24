import sys

import pandas as pd
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from misc.util import load_ui, resolve
from model.worm_data import load_data, save_data, show_load_dialog, show_save_dialog
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
    example_df = pd.DataFrame({"A": [4, 2], "B": [6, 9]})

    file_path = show_save_dialog()
    if file_path:
        save_data(file_path, example_df)

    file_path2 = show_load_dialog()

    if file_path2:
        loaded_df = load_data(file_path2)
        print(loaded_df)


# def main():
#     # df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

#     # save_worm_data("data/worm_data.parquet", df)

#     app = QApplication(sys.argv)
#     # Platform-independent style
#     app.setStyle("Fusion")
#     # Set global window icon
#     app.setWindowIcon(QIcon(resolve("ui/icon.ico")))
#     main = MainWindow()
#     main.window.show()

#     save_dialog()

#     sys.exit(app.exec())


if __name__ == "__main__":
    main()
