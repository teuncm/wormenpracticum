import sys

from PySide6.QtGui import QFont, QGuiApplication, QIcon, Qt
from PySide6.QtWidgets import QApplication

from app.controller.app_controller import AppController
from app.resource_path import resource_path
from app.view.view_helpers import set_font_size


def main():
    # Avoid scaling issues on high DPI displays.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/window/icon.ico")))

    # Normalize font style across platforms
    set_font_size(11)

    controller = AppController()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
