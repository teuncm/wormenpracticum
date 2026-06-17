from app.app_model import AppModel
from app.feature.filter.overview_view import OverviewView


class FilterController:
    """Controller for managing data filters in the app."""

    def __init__(self, app_model: AppModel, overview_view: OverviewView):
        self.app_model = app_model
        self.overview_view = overview_view

        self.connect_data_signals()
        self.update_ui_from_model()

    def connect_data_signals(self):
        self.overview_view.filterChanged.connect(self._on_view_filter_changed)
        self.app_model.filter_config_changed.connect(self.update_ui_from_model)

    def _on_view_filter_changed(self):
        self.app_model.update_filter_config(self.overview_view.to_filter_config())

    def update_ui_from_model(self):
        self.overview_view.update_from_config(self.app_model.filter_config)
