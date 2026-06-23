from PySide6.QtWidgets import QWidget

from app.shared.view_helpers import setup_ui_custom
from app.ui.generated.analyze_speed_window import Ui_AnalyzeSpeedWindow


class AnalyzeSpeedView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_AnalyzeSpeedWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)
