import json
from dataclasses import asdict

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFontDatabase,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from app.app_model import AppModel
from app.shared.view_helpers import setup_ui_custom
from app.ui.generated.debug_window import Ui_DebugWindow


class DebugView(QWidget):
    def __init__(self, app_model: AppModel):
        super().__init__()

        self.app_model = app_model
        self.ui = Ui_DebugWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.resize(800, 600)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.setup_widgets()
        self.refresh()

    def setup_widgets(self):
        toolbar = QHBoxLayout()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setPlaceholderText("Search")
        self.searchLineEdit.textChanged.connect(self._highlight_search_matches)
        self.searchLineEdit.returnPressed.connect(self.find_next)
        toolbar.addWidget(self.searchLineEdit)

        previous_button = QPushButton("Previous")
        previous_button.clicked.connect(self.find_previous)
        toolbar.addWidget(previous_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(self.find_next)
        toolbar.addWidget(next_button)

        self.searchResultLabel = QLabel()
        toolbar.addWidget(self.searchResultLabel)

        toolbar.addStretch()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_button)

        self.ui.verticalLayout.addLayout(toolbar)

        self.debugTextEdit = QPlainTextEdit()
        self.debugTextEdit.setReadOnly(True)
        self.debugTextEdit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        debug_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        if debug_font.pointSize() > 0:
            debug_font.setPointSize(debug_font.pointSize() + 1)
        self.debugTextEdit.setFont(debug_font)
        self.ui.verticalLayout.addWidget(self.debugTextEdit)

    def refresh(self):
        cursor = self.debugTextEdit.textCursor()
        cursor_position = cursor.position()
        vertical_scroll = self.debugTextEdit.verticalScrollBar().value()
        horizontal_scroll = self.debugTextEdit.horizontalScrollBar().value()

        self.debugTextEdit.setPlainText(
            json.dumps(self._app_model_snapshot(), indent=2, default=str)
        )
        cursor = QTextCursor(self.debugTextEdit.document())
        cursor.setPosition(min(cursor_position, len(self.debugTextEdit.toPlainText())))
        self.debugTextEdit.setTextCursor(cursor)
        self.debugTextEdit.verticalScrollBar().setValue(vertical_scroll)
        self.debugTextEdit.horizontalScrollBar().setValue(horizontal_scroll)
        self._highlight_search_matches()

    def find_next(self):
        self._find_search_text()

    def find_previous(self):
        self._find_search_text(QTextDocument.FindFlag.FindBackward)

    def _find_search_text(self, flags=QTextDocument.FindFlag(0)):
        search_text = self.searchLineEdit.text()
        if not search_text:
            return

        if self.debugTextEdit.find(search_text, flags):
            return

        cursor = self.debugTextEdit.textCursor()
        if flags & QTextDocument.FindFlag.FindBackward:
            cursor.movePosition(QTextCursor.MoveOperation.End)
        else:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.debugTextEdit.setTextCursor(cursor)
        self.debugTextEdit.find(search_text, flags)

    def _highlight_search_matches(self):
        search_text = self.searchLineEdit.text()
        if not search_text:
            self.debugTextEdit.setExtraSelections([])
            self.searchResultLabel.setText("")
            return

        selections = []
        cursor = QTextCursor(self.debugTextEdit.document())
        match_format = QTextCharFormat()
        match_format.setBackground(QColor("#fff59d"))
        match_count = 0

        while True:
            cursor = self.debugTextEdit.document().find(search_text, cursor)
            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = match_format
            selections.append(selection)
            match_count += 1

        self.debugTextEdit.setExtraSelections(selections)
        self.searchResultLabel.setText(f"{match_count} match(es)")

    def _app_model_snapshot(self) -> dict:
        return {
            "stim_config": asdict(self.app_model.stim_config),
            "protocol_config": asdict(self.app_model.protocol_config),
            "filter_config": asdict(self.app_model.filter_config),
            "experiment_config": self.app_model.experiment_config,
            "experiment_metadata": self.app_model.experiment_metadata,
        }
