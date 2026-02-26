import sys

from app.controller.main_controller import MainController
from app.utility_functions import resource_path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/window/icon.ico")))

    font = QFont()
    font.setStyleStrategy(
        QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality
    )
    app.setFont(font)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    mainController = MainController()
    mainController.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
