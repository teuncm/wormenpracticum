from app.controller.pulse_controller import PulseController
from app.model.app_model import AppModel
from app.model.nidaq_constants import NI_DAQ_DISCOVERY_POLL_INTERVAL_MS
from app.model.nidaq_model import NidaqModel
from app.view.about_view import AboutView
from app.view.analyze_view import AnalyzeView
from app.view.main_view import MainView
from app.view.protocol_view import ProtocolView
from app.view.pulse_view import PulseView
from app.view.smooth_view import SmoothView
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


class AppController:
    def __init__(self):
        self.init_mvc()

        self.connect_data_signals()
        self.connect_main_view_open_signals()

        self.init_nidaq()

    def init_mvc(self):
        """Initialize the model and view components."""
        self.app_model = AppModel()
        self.nidaq_model = NidaqModel()

        self.main_view = MainView()
        self.pulse_view = PulseView()
        self.protocol_view = ProtocolView()
        self.about_view = AboutView()
        self.analyze_view = AnalyzeView()
        self.smooth_view = SmoothView()

        self.pulse_controller = PulseController(self.app_model, self.pulse_view)

    def connect_main_view_open_signals(self):
        """Connect signals for opening views from the main view."""
        self.main_view.ui.actionAbout.triggered.connect(self.about_view.show)
        self.main_view.ui.actionAnalyze.triggered.connect(self.analyze_view.show)
        self.main_view.ui.actionSmoothing.triggered.connect(self.smooth_view.show)
        self.main_view.ui.actionImpulse.triggered.connect(self.pulse_view.show)
        self.main_view.ui.actionProtocol.triggered.connect(self.protocol_view.show)

    def connect_data_signals(self):
        """Data signals are owned by feature controllers."""
        return

    def init_nidaq(self):
        """Initialize nidaq connection polling."""
        self.refresh_nidaq_status()
        self.nidaq_status_timer = QTimer(self.main_view)
        self.nidaq_status_timer.setInterval(NI_DAQ_DISCOVERY_POLL_INTERVAL_MS)
        self.nidaq_status_timer.timeout.connect(self.refresh_nidaq_status)
        self.nidaq_status_timer.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

    def start(self):
        """Start the controller by showing the main view."""
        self.main_view.show()

    def refresh_nidaq_status(self):
        """Refresh the nidaq discovery status and update the main view."""
        self.nidaq_model.refresh_discovery_status()
        self.main_view.set_nidaq_status(self.nidaq_model.nidaq_status)

    def shutdown(self):
        """Clean up resources on application shutdown."""
        self.nidaq_status_timer.stop()
