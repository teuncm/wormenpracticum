from app.app_model import AppModel
from app.feature.acquisition.protocol_view import ProtocolView


class ProtocolController:
	def __init__(self, app_model: AppModel, protocol_view: ProtocolView):
		self.app_model = app_model
		self.protocol_view = protocol_view

		self.connect_data_signals()
		self.update_ui_from_model()

	def connect_data_signals(self):
		"""Data signals are owned by feature controllers."""
		self.protocol_view.run_requested.connect(self._on_run_requested)
		self.protocol_view.protocolChanged.connect(self._on_view_protocol_changed)
		self.app_model.protocol_config_changed.connect(self.update_ui_from_model)

	def _on_run_requested(self):
		"""Run-request handler placeholder for future NI-DAQ integration."""
		return

	def _on_view_protocol_changed(self):
		self.app_model.update_protocol_config(self.protocol_view.to_config())

	def update_ui_from_model(self):
		self.protocol_view.update_from_config(self.app_model.protocol_config)
