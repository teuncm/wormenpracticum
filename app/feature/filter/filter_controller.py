from app.app_model import AppModel
from app.feature.acquisition.protocol_view import ProtocolView


class FilterController:
    """Controller for managing data filters in the app."""

    def __init__(self, app_model: AppModel, protocol_view: ProtocolView):
        self.app_model = app_model
        self.protocol_view = protocol_view

        self.connect_data_signals()
        self.update_ui_from_model()

    def connect_data_signals(self):
        self.protocol_view.filterChanged.connect(self._on_view_filter_changed)
        self.app_model.filter_config_changed.connect(self.update_ui_from_model)

    def _on_view_filter_changed(self):
        self.app_model.update_filter_config(self.protocol_view.to_filter_config())

    def update_ui_from_model(self):
        self.protocol_view.update_filter_from_config(self.app_model.filter_config)
