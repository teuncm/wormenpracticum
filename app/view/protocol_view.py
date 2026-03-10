from app.window.ui_protocol_window import Ui_ProtocolWindow
from PySide6.QtWidgets import (
    QDialog,
)


class ProtocolView(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)
