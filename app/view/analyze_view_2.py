from PySide6.QtWidgets import QWidget

from app.view.view_helpers import setup_ui_custom
from app.window.ui_analyze_window_2 import Ui_AnalyzeWindow2


class AnalyzeView2(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeWindow2()
        self.ui.setupUi(self)

        setup_ui_custom(self)
