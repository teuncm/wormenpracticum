from PySide6.QtWidgets import QWidget

from app.view.view_helpers import create_title, main_layout_setup
from app.window.ui_analyze_window_2 import Ui_AnalyzeWindow2


class AnalyzeView2(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeWindow2()
        self.ui.setupUi(self)

        main_layout_setup(self.ui.horizontalLayout)

        self.ui.leftLayout.insertWidget(0, create_title("Controls"))
        self.ui.rightLayout.insertWidget(0, create_title("Overview"))
