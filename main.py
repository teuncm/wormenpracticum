import sys

from PySide6.QtGui import QGuiApplication, QIcon, Qt
from PySide6.QtWidgets import QApplication

from app.app_controller import AppController
from app.shared.resource_path import resource_path
from app.shared.view_helpers import set_font_size


def main():
    # Avoid scaling issues on high DPI displays.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/ui/icon.ico")))

    # Normalize font style across platforms
    set_font_size(11)

    controller = AppController()
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
