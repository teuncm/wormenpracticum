import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.utility_functions import resolve_project
from app.view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resolve_project("app/ui/icon.ico")))
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
