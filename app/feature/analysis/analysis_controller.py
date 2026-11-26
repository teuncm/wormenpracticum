from typing import Protocol

import pandas as pd
from PySide6.QtWidgets import QTabWidget, QWidget

from app.app_model import AppModel
from app.shared.deferred_tab_draw import DeferredTabDraw


class RecordingView(Protocol):
    """The recording input shared by the analysis tabs."""

    def set_data(
        self, data: pd.DataFrame | None, metadata: dict, config: dict
    ) -> None: ...

    def parentWidget(self) -> QWidget | None: ...


class AnalysisController:
    """Keep an analysis view synchronized with the current filtered recording."""

    def __init__(
        self,
        app_model: AppModel,
        view: RecordingView,
        *,
        tabs: QTabWidget | None = None,
    ):
        self.app_model = app_model
        self.view = view

        # The application gives each analysis view its own frame inside the tab widget.
        page = view.parentWidget() if tabs is not None else None
        self._draw = DeferredTabDraw(self._draw_recording, page, tabs)
        self.app_model.experiment_data_changed.connect(self.update_ui_from_model)

        self.update_ui_from_model()

    def update_ui_from_model(self) -> None:
        """Mark the view stale and redraw immediately if its tab is active."""
        self._draw.request()

    def _draw_recording(self) -> None:
        # Read from the model at draw time so hidden tabs only render the latest update.
        self.view.set_data(
            self.app_model.filtered_data_df,
            self.app_model.experiment_metadata,
            self.app_model.experiment_config,
        )
