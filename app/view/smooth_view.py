from app.window.ui_smooth_window import Ui_Form as Ui_SmoothWindow
from PySide6.QtWidgets import QWidget


class SmoothView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_SmoothWindow()
        self.ui.setupUi(self)
