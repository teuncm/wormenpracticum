import sys

from app.controller.app_controller import AppController
from app.utility_functions import resource_path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/window/icon.ico")))

    controller = AppController()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
