from app.window.ui_protocol_window import Ui_ProtocolWindow
from PySide6.QtWidgets import (
    QWidget,
)


class ProtocolView(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)
