import sys

from app.controller.app_controller import AppController
from app.utility_functions import resource_path
from PySide6.QtGui import QFont, QGuiApplication, QIcon, Qt
from PySide6.QtWidgets import QApplication


def main():
    # Scale better on high-resolution displays
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/window/icon.ico")))

    # Normalize font style across platforms
    font = app.font()
    font.setPointSize(11)
    font.setWeight(QFont.Weight.Normal)
    app.setFont(font)

    controller = AppController()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
