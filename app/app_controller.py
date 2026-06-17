import dataclasses
import getpass
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import cast

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.app_view import AppView
from app.feature.about.about_view import AboutView
from app.feature.acquisition.protocol_controller import ProtocolController
from app.feature.acquisition.protocol_view import ProtocolView
from app.feature.analysis.analyze_view import AnalyzeView
from app.feature.analysis.analyze_view_2 import AnalyzeView2
from app.feature.debug.debug_view import DebugView
from app.feature.filter.filter_controller import FilterController
from app.feature.filter.filter_view import FilterView
from app.feature.filter.overview_view import OverviewView
from app.feature.nidaq.nidaq_constants import NI_DAQ_DISCOVERY_POLL_INTERVAL_MS
from app.feature.nidaq.nidaq_controller import NidaqController
from app.feature.nidaq.nidaq_model import NidaqModel
from app.feature.preferences.preferences_view import PreferencesView
from app.feature.stimulus.stimulus_controller import StimulusController
from app.feature.stimulus.stimulus_view import StimulusView
from app.shared import data_dialog, data_io
from app.shared.constants import (
    APP_ORG,
    APP_TITLE,
    DEFAULT_FILTER_CONFIG,
    DEFAULT_PROTOCOL_CONFIG,
    DEFAULT_STIMULUS_CONFIG,
)
from app.shared.view_helpers import info_box, set_font_size


class AppController:
    def __init__(self):
        self.settings = QSettings(APP_ORG, APP_TITLE)

        self.init_mvc()
        self.connect_data_signals()

        # self.save_state(.json")

        # self.init_nidaq()

        state = self.app_model.export_state()

        pprint(state)

        self.app_model.import_state(state)

        self.restore_preferences()

    def init_mvc(self):
        """Initialize mvc components."""
        self.app_model = AppModel()

        self.nidaq_model = NidaqModel()
        self.nidaq_controller = NidaqController(self.nidaq_model, self.app_model)

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
        self.filter_controller = FilterController(self.app_model, self.overview_view)

    def restore_preferences(self):
        point_size = cast(int, self.settings.value("ui/font_size", 10, int))
        set_font_size(point_size)

    def connect_data_signals(self):
        """Connect signals for loading and saving data."""
        self.app_model.experiment_data_changed.connect(self.update_main_plot)
        self.app_view.data_load_requested.connect(self.load_experiment_data)
        self.app_view.data_save_requested.connect(self.save_experiment_data)
        self.app_view.stimulus_load_requested.connect(self.load_stimulus_state)
        self.app_view.stimulus_save_requested.connect(self.save_stimulus_state)
        self.app_view.protocol_load_requested.connect(self.load_protocol_state)
        self.app_view.protocol_save_requested.connect(self.save_protocol_state)
        self.app_view.filter_load_requested.connect(self.load_filter_state)
        self.app_view.filter_save_requested.connect(self.save_filter_state)
        self.app_view.stimulus_reset_requested.connect(self.reset_stimulus_state)
        self.app_view.protocol_reset_requested.connect(self.reset_protocol_state)
        self.app_view.filter_reset_requested.connect(self.reset_filter_state)
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

    def save_stimulus_state(self):
        self.save_named_state("stimulus", "stim_config")

    def load_stimulus_state(self):
        self.load_named_state("stimulus", "stim_config")

    def save_protocol_state(self):
        self.save_named_state("protocol", "protocol_config")

    def load_protocol_state(self):
        self.load_named_state("protocol", "protocol_config")

    def save_filter_state(self):
        self.save_named_state("filter", "filter_config")

    def load_filter_state(self):
        self.load_named_state("filter", "filter_config")

    def reset_stimulus_state(self):
        self.app_model.import_state({"stim_config": DEFAULT_STIMULUS_CONFIG.to_dict()})

    def reset_protocol_state(self):
        self.app_model.import_state(
            {"protocol_config": dataclasses.asdict(DEFAULT_PROTOCOL_CONFIG)}
        )

    def reset_filter_state(self):
        self.app_model.import_state(
            {"filter_config": dataclasses.asdict(DEFAULT_FILTER_CONFIG)}
        )

    def save_named_state(self, state_name: str, state_key: str):
        """Save one app state section to a typed JSON file."""
        filename = data_dialog.show_save_json_dialog()
        if filename is None:
            info_box(message="No file name was given.").exec()
            return

        filename = self._state_filename(filename, state_name)
        state = {state_key: self.app_model.export_state()[state_key]}
        msg = data_io.write_metadata(filename, state)
        if msg:
            info_box(message=f"Error saving {state_name}: {msg}").exec()

    def load_named_state(self, state_name: str, state_key: str):
        """Load one app state section from JSON into the app model."""
        filename = data_dialog.show_load_json_dialog()
        if filename is None:
            info_box(message="No file was selected.").exec()
            return

        state = data_io.read_metadata(filename)
        if isinstance(state, str):
            info_box(message=f"Error loading {state_name}: {state}").exec()
            return

        if state_key not in state:
            state = {state_key: state}

        self.app_model.import_state(state)

    def _state_filename(self, filename: str, state_name: str) -> str:
        path = Path(filename)
        base_path = path.with_suffix("")
        for suffix in (".stimulus", ".protocol", ".filter"):
            if base_path.name.endswith(suffix):
                base_path = base_path.with_name(base_path.name[: -len(suffix)])
                break

        return str(base_path.with_name(f"{base_path.name}.{state_name}.json"))

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
