from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QCursor, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QMainWindow,
    QStyle,
    QStyleOptionTab,
    QStylePainter,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.shared.constants import APP_TITLE
from app.shared.view_helpers import set_global_plot_config
from app.ui.generated.app_window import Ui_AppWindow


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
        return QSize(size.height(), size.width() + 50)

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
                    Qt.AlignmentFlag.AlignCenter.value,
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


class HorizontalTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered_index = -1
        self.setShape(QTabBar.Shape.RoundedNorth)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMouseTracking(True)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        return QSize(size.width() + 80, size.height() + 5)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        try:
            for index in range(self.count()):
                option = QStyleOptionTab()
                self.initStyleOption(option, index)
                option.text = " ".join(option.text.splitlines())
                if index == self._hovered_index and self.isTabEnabled(index):
                    option.state |= QStyle.StateFlag.State_MouseOver
                else:
                    option.state &= ~QStyle.StateFlag.State_MouseOver

                option.shape = QTabBar.Shape.RoundedNorth

                painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)

                rect = option.rect.adjusted(8, 0, -8, 0)

                font = painter.font()
                font.setPointSize(10)
                painter.setFont(font)

                painter.drawItemText(
                    rect,
                    Qt.AlignmentFlag.AlignCenter.value,
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
    stimulus_load_requested = Signal()
    stimulus_save_requested = Signal()
    protocol_load_requested = Signal()
    protocol_save_requested = Signal()
    filter_load_requested = Signal()
    filter_save_requested = Signal()
    debug_requested = Signal()
    preferences_requested = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_AppWindow()
        self.ui.setupUi(self)

        set_global_plot_config()

        tabs = self.ui.tabWidget
        tabs.clear()
        self.set_tab_orientation(vertical=False)
        tabs.setDocumentMode(True)
        tabs.currentChanged.connect(self._update_window_title)
        self._update_window_title()

        self.ui.menuFile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.ui.actionLoad_data.triggered.connect(self.on_load_triggered)
        self.ui.actionSave_data.triggered.connect(self.on_save_triggered)
        self.ui.actionLoad_stimulus.triggered.connect(
            self.stimulus_load_requested.emit
        )
        self.ui.actionSave_stimulus.triggered.connect(
            self.stimulus_save_requested.emit
        )
        self.ui.actionLoad_protocol.triggered.connect(
            self.protocol_load_requested.emit
        )
        self.ui.actionSave_protocol.triggered.connect(
            self.protocol_save_requested.emit
        )
        self.ui.actionLoad_filter.triggered.connect(self.filter_load_requested.emit)
        self.ui.actionSave_filter.triggered.connect(self.filter_save_requested.emit)
        self.ui.actionDebug.triggered.connect(self.debug_requested.emit)
        self.ui.actionPreferences.triggered.connect(self.preferences_requested.emit)
        self.ui.actionExit.triggered.connect(self.close)

    def clear_tabs(self):
        self.ui.tabWidget.clear()
        self._update_window_title()

    def set_tab_orientation(self, vertical: bool):
        tabs = self.ui.tabWidget
        if vertical:
            tabs.setTabBar(VerticalTabBar())
            tabs.setTabPosition(QTabWidget.TabPosition.West)
            tabs.tabBar().setShape(QTabBar.Shape.RoundedWest)
            tabs.setDocumentMode(True)
        else:
            tabs.setTabBar(HorizontalTabBar())
            tabs.setTabPosition(QTabWidget.TabPosition.North)
            tabs.tabBar().setShape(QTabBar.Shape.RoundedNorth)
            tabs.setDocumentMode(False)

    def add_tab(self, widget: QWidget, label: str):
        self.ui.tabWidget.addTab(self._create_tab_page_frame(widget), label)
        self._update_window_title()

    def _create_tab_page_frame(self, widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        frame.setAutoFillBackground(False)

        widget.setBackgroundRole(QPalette.ColorRole.Window)
        widget.setAutoFillBackground(True)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget)

        return frame

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
