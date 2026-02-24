import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.utility_functions import resource_path
from app.view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/ui/icon.ico")))
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
