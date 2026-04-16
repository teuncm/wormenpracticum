from app.window.ui_analyze_window import Ui_Form as Ui_AnalyzeWindow
from PySide6.QtWidgets import QWidget


class AnalyzeView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeWindow()
        self.ui.setupUi(self)
