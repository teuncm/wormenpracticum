from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QCursor, QPalette
from PySide6.QtWidgets import (
    QMainWindow,
    QStyle,
    QStyleOptionTab,
    QStylePainter,
    QTabBar,
    QTabWidget,
    QWidget,
)

from app.constants import APP_TITLE
from app.view.view_helpers import set_global_plot_config
from app.window.ui_app_window import Ui_AppWindow


class VerticalTabBar(QTabBar):
    """Custom tab bar to display tabs on the left side of the window
    with the correct text rotation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered_index = -1
        self.setShape(QTabBar.Shape.RoundedWest)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMouseTracking(True)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        # Swap width/height because west tabs are normally vertical.
        return QSize(size.height() - 12, size.width() + 50)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        try:
            for index in range(self.count()):
                option = QStyleOptionTab()
                self.initStyleOption(option, index)
                if index == self._hovered_index and self.isTabEnabled(index):
                    option.state |= QStyle.StateFlag.State_MouseOver
                else:
                    option.state &= ~QStyle.StateFlag.State_MouseOver

                # Important: draw the tab as a WEST tab.
                # This makes the selected tab connect to the page on the east/right side.
                option.shape = QTabBar.Shape.RoundedWest

                painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)

                rect = option.rect.adjusted(8, 0, -8, 0)

                font = painter.font()
                font.setPointSize(10)
                painter.setFont(font)

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

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._set_hovered_index(self.tabAt(event.position().toPoint()))

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._set_hovered_index(-1)

    def _set_hovered_index(self, index):
        if index == self._hovered_index:
            return

        previous_index = self._hovered_index
        self._hovered_index = index

        if previous_index >= 0:
            self.update(self.tabRect(previous_index))
        if index >= 0:
            self.update(self.tabRect(index))


class AppView(QMainWindow):
    data_load_requested = Signal()
    data_save_requested = Signal()
    debug_requested = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_AppWindow()
        self.ui.setupUi(self)

        set_global_plot_config()

        tabs = self.ui.tabWidget
        tabs.clear()
        tabs.setTabBar(VerticalTabBar())
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        tabs.tabBar().setShape(QTabBar.Shape.RoundedWest)
        tabs.currentChanged.connect(self._update_window_title)
        self._update_window_title()

        self.ui.menuFile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.ui.actionLoad_data.triggered.connect(self.on_load_triggered)
        self.ui.actionSave_data.triggered.connect(self.on_save_triggered)
        self.ui.actionDebug.triggered.connect(self.debug_requested.emit)
        self.ui.actionExit.triggered.connect(self.close)

    def clear_tabs(self):
        self.ui.tabWidget.clear()
        self._update_window_title()

    def add_tab(self, widget: QWidget, label: str):
        index = self.ui.tabWidget.addTab(widget, label)
        self.ui.tabWidget.setTabToolTip(index, self._format_tab_name(label))
        self._update_window_title()

    def set_current_tab_index(self, index: int):
        self.ui.tabWidget.setCurrentIndex(index)
        self._update_window_title()

    def _update_window_title(self, index: int | None = None):
        if index is None:
            index = self.ui.tabWidget.currentIndex()

        tab_name = ""
        if index >= 0:
            tab_name = self._format_tab_name(self.ui.tabWidget.tabText(index))

        if tab_name:
            self.setWindowTitle(f"{APP_TITLE} - {tab_name}")
        else:
            self.setWindowTitle(APP_TITLE)

    def _format_tab_name(self, label: str) -> str:
        return " ".join(label.split())

    def on_load_triggered(self, checked=False):
        self.data_load_requested.emit()

    def on_save_triggered(self, checked=False):
        self.data_save_requested.emit()
