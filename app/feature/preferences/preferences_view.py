from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from app.shared.view_helpers import setup_ui_custom
from app.ui.generated.preferences_window import Ui_PreferencesWindow


class PreferencesView(QWidget):
    font_size_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self.ui = Ui_PreferencesWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.ui.fontSizeSpinBox.valueChanged.connect(self.font_size_changed.emit)

    def font_size(self) -> int:
        return self.ui.fontSizeSpinBox.value()

    def set_font_size(self, point_size: int):
        self.ui.fontSizeSpinBox.setValue(point_size)
