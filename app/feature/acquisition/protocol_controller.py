from app.app_model import AppModel
from app.feature.acquisition.protocol_view import ProtocolView


class ProtocolController:
	def __init__(self, app_model: AppModel, protocol_view: ProtocolView):
		self.app_model = app_model
		self.protocol_view = protocol_view

		self.connect_data_signals()

	def connect_data_signals(self):
		"""Data signals are owned by feature controllers."""
		self.protocol_view.run_requested.connect(self._on_run_requested)

	def _on_run_requested(self):
		"""Run-request handler placeholder for future NI-DAQ integration."""
		return
