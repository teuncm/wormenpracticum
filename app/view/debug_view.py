import json

import pandas as pd
from app.model.app_model import AppModel
from app.view.view_helpers import create_title
from app.window.ui_debug_window import Ui_DebugWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QPushButton, QWidget


class DebugView(QWidget):
    def __init__(self, app_model: AppModel):
        super().__init__()

        self.app_model = app_model
        self.ui = Ui_DebugWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.setup_widgets()
        self.refresh()

    def setup_widgets(self):
        self.ui.verticalLayout.addWidget(create_title("App model debug"))

        toolbar = QHBoxLayout()
        toolbar.addStretch()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_button)

        self.ui.verticalLayout.addLayout(toolbar)

        self.debugTextEdit = QPlainTextEdit()
        self.debugTextEdit.setReadOnly(True)
        self.debugTextEdit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.debugTextEdit.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        self.ui.verticalLayout.addWidget(self.debugTextEdit)

    def refresh(self):
        self.debugTextEdit.setPlainText(
            json.dumps(self._app_model_snapshot(), indent=2, default=str)
        )

    def _app_model_snapshot(self) -> dict:
        stim_generator = self.app_model.stim_generator

        return {
            "stim_config": self.app_model.stim_config.to_dict(),
            "stim_generator": {
                "n_stims": len(stim_generator.stims),
                "x_bounds": self.app_model.get_x_bounds(),
                "y_bounds": self.app_model.get_y_bounds(),
            },
            "experiment_config": self.app_model.experiment_config,
            "experiment_metadata": self.app_model.experiment_metadata,
            "raw_data": self._dataframe_snapshot(self.app_model.raw_data_df),
            "filtered_data": self._dataframe_snapshot(self.app_model.filtered_data_df),
        }

    def _dataframe_snapshot(self, df: pd.DataFrame | None) -> dict:
        if df is None:
            return {
                "loaded": False,
            }

        return {
            "loaded": True,
            "shape": list(df.shape),
            "columns": [str(column) for column in df.columns],
            "dtypes": {str(column): str(dtype) for column, dtype in df.dtypes.items()},
            "memory_bytes": int(df.memory_usage(deep=True).sum()),
        }
