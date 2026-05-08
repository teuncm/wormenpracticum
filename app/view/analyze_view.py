from PySide6.QtWidgets import QWidget

from app.view.view_helpers import main_layout_setup
from app.window.ui_analyze_window import Ui_Form as Ui_AnalyzeWindow


class AnalyzeView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeWindow()
        self.ui.setupUi(self)

        main_layout_setup(self.ui.horizontalLayout)
