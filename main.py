import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.controller.main_controller import MainController
from app.utility_functions import resource_path


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/ui/icon.ico")))

    controller = MainController()
    controller.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
