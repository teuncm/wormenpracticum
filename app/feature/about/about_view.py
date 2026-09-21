from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from app.shared.view_helpers import setup_ui_custom
from app.ui.generated.about_window import Ui_AboutWindow


class AboutView(QWidget):
    """Standalone window with app credits and filter information."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_AboutWindow()
        self.ui.setupUi(self)
        setup_ui_custom(self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
