import sys

from app.controller.main_controller import MainController
from app.model.main_model import MainModel
from app.utility_functions import resource_path
from app.view.main_view import MainView
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # Platform-independent style
    app.setStyle("Fusion")
    # Global window icon
    app.setWindowIcon(QIcon(resource_path("app/window/icon.ico")))

    mainView = MainView()
    mainModel = MainModel()
    mainController = MainController(mainModel, mainView)
    mainController.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
