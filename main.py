import sys

from PySide6.QtGui import QGuiApplication, QIcon, Qt
from PySide6.QtWidgets import QApplication

from app.app_controller import AppController
from app.shared.resource_path import resource_path
from app.shared.settings import (
    configure_app_identity,
    configure_windows_app_user_model_id,
)
from app.shared.view_helpers import set_font_size


def main():
    # Avoid scaling issues on high DPI displays.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    configure_windows_app_user_model_id()
    configure_app_identity()

    app = QApplication(sys.argv)

    # Global window icon
    app_icon = QIcon(resource_path("app/ui/icon.ico"))
    app.setWindowIcon(app_icon)

    # Normalize font style across platforms
    set_font_size(11)

    controller = AppController()
    controller.app_view.setWindowIcon(app_icon)
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
