from app.controller.stimulus_controller import StimulusController
from app.model.app_model import AppModel
from app.model.nidaq.nidaq_constants import NI_DAQ_DISCOVERY_POLL_INTERVAL_MS
from app.model.nidaq.nidaq_model import NidaqModel
from app.view.about_view import AboutView
from app.view.analyze_view import AnalyzeView
from app.view.app_view import AppView
from app.view.protocol_view import ProtocolView
from app.view.smooth_view import SmoothView
from app.view.stimulus_view import StimulusView
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


class AppController:
    def __init__(self):
        self.init_mvc()

        self.connect_app_view_open_signals()
        self.connect_data_signals()

        self.init_nidaq()

    def init_mvc(self):
        """Initialize mvc components."""
        self.app_model = AppModel()
        self.nidaq_model = NidaqModel()

        self.app_view = AppView()
        self.stimulus_view = StimulusView()
        self.protocol_view = ProtocolView()
        self.about_view = AboutView()
        self.analyze_view = AnalyzeView()
        self.smooth_view = SmoothView()

        self.stimulus_controller = StimulusController(
            self.app_model, self.stimulus_view
        )

    def connect_app_view_open_signals(self):
        """Connect signals for opening views from the app view."""
        self.app_view.ui.actionAbout.triggered.connect(self.about_view.show)
        self.app_view.ui.actionAnalyze.triggered.connect(self.analyze_view.show)
        self.app_view.ui.actionSmoothing.triggered.connect(self.smooth_view.show)
        self.app_view.ui.actionImpulse.triggered.connect(self.stimulus_view.show)
        self.app_view.ui.actionProtocol.triggered.connect(self.protocol_view.show)

    def connect_data_signals(self):
        """Connect signals for loading and saving data."""
        self.app_model.experiment_data_changed.connect(self.update_main_plot)

    def update_main_plot(self):
        """Update the main plot with the latest experiment data."""
        if self.app_model.experiment_df is not None:
            self.app_view.plot_data(self.app_model.experiment_df)

    def init_nidaq(self):
        """Initialize nidaq connection polling."""
        self.refresh_nidaq_status()
        self.nidaq_status_timer = QTimer(self.app_view)
        self.nidaq_status_timer.setInterval(NI_DAQ_DISCOVERY_POLL_INTERVAL_MS)
        self.nidaq_status_timer.timeout.connect(self.refresh_nidaq_status)
        self.nidaq_status_timer.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

    def start(self):
        """Start the application by showing the main view."""
        self.app_view.show()

    def refresh_nidaq_status(self):
        """Refresh the nidaq discovery status and update the main view."""
        self.nidaq_model.refresh_discovery_status()
        self.app_view.set_nidaq_status(self.nidaq_model.nidaq_status)

    def shutdown(self):
        """Clean up resources on application shutdown."""
        self.nidaq_status_timer.stop()
