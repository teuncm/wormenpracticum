from app.view.view_helpers import set_global_plot_config
from app.window.ui_app_window import Ui_AppWindow
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QMainWindow,
    QStyle,
    QStyleOptionTab,
    QStylePainter,
    QTabBar,
    QTabWidget,
    QWidget,
)


class HorizontalTabBar(QTabBar):
    """Custom tab bar to display tabs on the left side of the window
    with the correct text rotation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setShape(QTabBar.Shape.RoundedWest)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        # Swap width/height because west tabs are normally vertical.
        return QSize(size.height(), size.width() + 60)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        try:
            for index in range(self.count()):
                option = QStyleOptionTab()
                self.initStyleOption(option, index)

                # Important: draw the tab as a WEST tab.
                # This makes the selected tab connect to the page on the east/right side.
                option.shape = QTabBar.Shape.RoundedWest

                painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)

                rect = option.rect.adjusted(8, 0, -8, 0)

                painter.drawItemText(
                    rect,
                    Qt.AlignmentFlag.AlignCenter.value | Qt.TextFlag.TextWordWrap.value,
                    option.palette,
                    bool(option.state & QStyle.StateFlag.State_Enabled),
                    option.text,
                    QPalette.ColorRole.ButtonText,
                )
        finally:
            painter.end()


class AppView(QMainWindow):
    data_load_requested = Signal()
    data_save_requested = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_AppWindow()
        self.ui.setupUi(self)

        set_global_plot_config()

        tabs = self.ui.tabWidget
        tabs.clear()
        tabs.setTabBar(HorizontalTabBar())
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        tabs.tabBar().setShape(QTabBar.Shape.RoundedWest)

        self.ui.actionLoad_data.triggered.connect(self.on_load_triggered)
        self.ui.actionSave_data.triggered.connect(self.on_save_triggered)
        self.ui.actionExit.triggered.connect(self.close)

    def clear_tabs(self):
        self.ui.tabWidget.clear()

    def add_tab(self, widget: QWidget, label: str):
        self.ui.tabWidget.addTab(widget, label)

    def set_current_tab_index(self, index: int):
        self.ui.tabWidget.setCurrentIndex(index)

    def on_load_triggered(self, checked=False):
        self.data_load_requested.emit()

    def on_save_triggered(self, checked=False):
        self.data_save_requested.emit()
