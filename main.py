import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from misc.util import load_ui, resolve


class MainWindow:
    def __init__(self):
        self.window = load_ui(resolve("ui/main_window.ui"))

        self.window.pushButton.clicked.connect(self.open_second)
        self.window.slider1.valueChanged.connect(self.window.slider1Label.setNum)

    def open_second(self):
        self.second_window = load_ui(resolve("ui/tool_view.ui"))
        self.second_window.show()


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Set global window icon
    app.setWindowIcon(QIcon(resolve("ui/icon.ico")))
    main = MainWindow()
    main.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
