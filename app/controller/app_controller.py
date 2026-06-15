import dataclasses
import getpass
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import cast

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication

from app.constants import APP_ORG, APP_TITLE
from app.controller.filter_controller import FilterController
from app.controller.nidaq_controller import NidaqController
from app.controller.protocol_controller import ProtocolController
from app.controller.stimulus_controller import StimulusController
from app.model import data_io
from app.model.app_model import AppModel
from app.model.nidaq.nidaq_constants import NI_DAQ_DISCOVERY_POLL_INTERVAL_MS
from app.model.nidaq.nidaq_model import NidaqModel
from app.view import data_dialog
from app.view.about_view import AboutView
from app.view.analyze_view import AnalyzeView
from app.view.analyze_view_2 import AnalyzeView2
from app.view.app_view import AppView
from app.view.debug_view import DebugView
from app.view.filter_view import FilterView
from app.view.overview_view import OverviewView
from app.view.preferences_view import PreferencesView
from app.view.protocol_view import ProtocolView
from app.view.stimulus_view import StimulusView
from app.view.view_helpers import info_box, set_font_size


class AppController:
    def __init__(self):
        self.settings = QSettings(APP_ORG, APP_TITLE)

        self.init_mvc()

        # self.connect_data_signals()

        # self.save_state(.json")

        # self.init_nidaq()

        pprint(self.app_model.export_state())

        self.restore_preferences()

    def init_mvc(self):
        """Initialize mvc components."""
        self.app_model = AppModel()

        self.nidaq_model = NidaqModel()
        self.nidaq_controller = NidaqController(self.nidaq_model, self.app_model)

        self.filter_controller = FilterController(self.app_model)

        self.app_view = AppView()
        self.stimulus_view = StimulusView()
        self.protocol_view = ProtocolView()
        self.overview_view = OverviewView()
        self.about_view = AboutView()
        self.analyze_view = AnalyzeView()
        self.analyze_view_2 = AnalyzeView2()
        self.filter_view = FilterView()
        self.debug_view = DebugView(self.app_model)
        self.preferences_view = PreferencesView()

        self.app_view.clear_tabs()
        self.app_view.add_tab(self.stimulus_view, "Stimulus\ndesigner")
        self.app_view.add_tab(self.protocol_view, "Data\nacquisition")
        self.app_view.add_tab(self.overview_view, "Filter")
        self.app_view.add_tab(self.analyze_view, "Analyze\npeaks")
        self.app_view.add_tab(self.analyze_view_2, "Analyze\nother")
        self.app_view.set_current_tab_index(2)

        self.stimulus_controller = StimulusController(
            self.app_model, self.stimulus_view
        )
        self.protocol_controller = ProtocolController(
            self.app_model, self.protocol_view
        )

    def restore_preferences(self):
        point_size = cast(int, self.settings.value("ui/font_size", 10, int))
        set_font_size(point_size)

    def connect_data_signals(self):
        """Connect signals for loading and saving data."""
        self.app_model.experiment_data_changed.connect(self.update_main_plot)
        self.app_view.data_load_requested.connect(self.load_experiment_data)
        self.app_view.data_save_requested.connect(self.save_experiment_data)
        self.app_view.debug_requested.connect(self.show_debug_view)
        self.app_view.preferences_requested.connect(self.show_preferences_view)
        self.protocol_view.run_requested.connect(self.run_magic)
        self.nidaq_model.discovery_state_changed.connect(self.update_nidaq_label)

    def run_magic(self):
        """In the magic function we will connect to a DAQ and send a hello world signal."""
        self.nidaq_controller.magic()

    def update_main_plot(self):
        """Update the main plot with the latest experiment data."""
        if self.app_model.raw_data_df is not None:
            self.overview_view.plot_data(self.app_model.raw_data_df)

    def init_nidaq(self):
        """Initialize nidaq connection polling."""
        self.nidaq_status_timer = QTimer(self.app_view)
        self.nidaq_status_timer.setInterval(NI_DAQ_DISCOVERY_POLL_INTERVAL_MS)
        self.nidaq_status_timer.timeout.connect(self.discover_nidaq_device)
        self.nidaq_status_timer.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.cleanup)

    def start(self):
        """Start the application by showing the main view."""
        self.app_view.show()
        # self.app_view.showMaximized()

    def cleanup(self):
        """Clean up resources on application shutdown."""
        self.nidaq_status_timer.stop()

    def discover_nidaq_device(self):
        """Refresh the nidaq discovery status."""
        self.nidaq_controller.discover()

    def update_nidaq_label(self):
        """Update the nidaq status label in the app view."""
        self.protocol_view.set_nidaq_status(self.nidaq_model.device_status)

    def show_debug_view(self):
        """Show the debug window and refresh its app model snapshot."""
        self.debug_view.refresh()
        self.debug_view.show()
        self.debug_view.raise_()
        self.debug_view.activateWindow()

    def show_preferences_view(self):
        """Show the preferences window."""
        self.preferences_view.show()
        self.preferences_view.raise_()
        self.preferences_view.activateWindow()

    def save_experiment_data(self):
        """Save experiment data to a file."""
        filename = data_dialog.show_save_dialog()
        if filename is None:
            info_box(message="No file name was given.").exec()
            return

        if self.app_model.raw_data_df is None:
            info_box(message="There is no data to save.").exec()
            return

        msg = data_io.write_data(filename, self.app_model.raw_data_df)
        self.save_experiment_metadata(filename)
        if msg:
            info_box(message=f"Error saving data: {msg}").exec()
        else:
            success_box = info_box(
                message="Data saved successfully. File location has been copied to the clipboard.",
            )
            success_box.setDetailedText(filename)
            success_box.exec()

            QApplication.clipboard().setText(filename)

    def load_experiment_data(self):
        filename = data_dialog.show_load_dialog()
        if filename is None:
            info_box(message="No file was selected.").exec()
            return

        df = data_io.read_data(filename)
        if isinstance(df, str):
            info_box(message=f"Error loading data: {df}").exec()
            return

        self.app_model.update_experiment_data(df)

    def save_state(self, filename):
        """Save the entire state of the application to a file."""
        state = {
            "stim_config": dataclasses.asdict(self.app_model.stim_config),
            "protocol_config": dataclasses.asdict(self.app_model.protocol_config),
            "filter_config": dataclasses.asdict(self.app_model.filter_config),
            "experiment_config": self.app_model.experiment_config,
            "experiment_metadata": self.app_model.experiment_metadata,
        }
        print(state)

    def save_experiment_metadata(self, filename):
        """Save experiment metadata to a file.
        Automatically called when saving experiment data."""
        base_filename = Path(filename).stem
        metadata_filename = str(Path(filename).with_suffix(".json"))
        now = datetime.now().astimezone()
        save_metadata = {
            "file": base_filename,
            "save_user": getpass.getuser(),
            "save_date": now.date().isoformat(),
            "save_time": now.timetz().isoformat(),
        }
        experiment_metadata = self.app_model.experiment_metadata or {}
        metadata_aggregate = {
            "metadata": save_metadata | experiment_metadata,
            "experiment_config": self.app_model.experiment_config,
            "stim_config": self.app_model.stim_config.to_dict(),
        }
        msg = data_io.write_metadata(metadata_filename, metadata_aggregate)
        if msg:
            info_box(message=f"Error saving metadata: {msg}").exec()
