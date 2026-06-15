from app.ui.generated.about_window import Ui_Form as Ui_AboutWindow
from PySide6.QtWidgets import QWidget


class AboutView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AboutWindow()
        self.ui.setupUi(self)
