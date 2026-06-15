import dataclasses

import pandas as pd
from PySide6.QtCore import QObject, Signal

from app.shared.constants import (
    DEFAULT_FILTER_CONFIG,
    DEFAULT_PROTOCOL_CONFIG,
    DEFAULT_STIMULUS_CONFIG,
)
from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator
from app.feature.filter.filter_config import FilterConfig


class AppModel(QObject):
    """AppModel contains all persistent app data and logic, acting as a single source of truth.
    It emits signals when data changes, allowing views to react and update accordingly."""

    #
    # Source state/data
    #

    stim_config: StimulusConfig
    protocol_config: ProtocolConfig
    filter_config: FilterConfig
    experiment_config: dict
    experiment_metadata: dict
    raw_data_df: pd.DataFrame | None

    #
    # Derived state/data
    #

    # The stimulus generator instance, created based on the current stimulus config
    stim_generator: StimulusGenerator
    # Filtered experiment data as DataFrame, cached after applying filters to raw data
    # If no filters have been applied, values are the same as raw_data_df
    filtered_data_df: pd.DataFrame | None

    #
    # Signals
    #

    # Emit when any of the configs changed. The changes will be reflected in the view.
    stim_config_changed = Signal()
    protocol_config_changed = Signal()
    filter_config_changed = Signal()

    # Emit when experiment data changed
    experiment_data_changed = Signal()

    def __init__(self):
        super().__init__()

        self.stim_config = DEFAULT_STIMULUS_CONFIG
        self.protocol_config = DEFAULT_PROTOCOL_CONFIG
        self.filter_config = DEFAULT_FILTER_CONFIG
        self.experiment_config = {}
        self.experiment_metadata = {}
        self.raw_data_df = None
        self.stim_generator = StimulusGenerator(self.stim_config)
        self.filtered_data_df = None

    def export_state(self):
        """Export the entire state of the application as a dictionary."""
        return {
            "stim_config": dataclasses.asdict(self.stim_config),
            "protocol_config": dataclasses.asdict(self.protocol_config),
            "filter_config": dataclasses.asdict(self.filter_config),
            "experiment_config": self.experiment_config,
            "experiment_metadata": self.experiment_metadata,
        }

    def import_state(self, state: dict):
        """Import source state information of the application from a dictionary, updating derived state
        information where needed."""
        if "stim_config" in state:
            self.stim_config = StimulusConfig(**state["stim_config"])
            self.stim_generator = StimulusGenerator(self.stim_config)
            self.stim_config_changed.emit()
        if "protocol_config" in state:
            self.protocol_config = ProtocolConfig(**state["protocol_config"])
            self.protocol_config_changed.emit()
        if "filter_config" in state:
            self.filter_config = FilterConfig(**state["filter_config"])
            self.filter_config_changed.emit()
        if "experiment_config" in state:
            self.experiment_config = state["experiment_config"]
        if "experiment_metadata" in state:
            self.experiment_metadata = state["experiment_metadata"]

    def update_experiment_data(self, df: pd.DataFrame):
        """Update experiment data with a new dataframe."""
        if self.raw_data_df is not None and self.raw_data_df.equals(df):
            return

        self.raw_data_df = df
        self.filtered_data_df = df
        self.experiment_data_changed.emit()

    def update_stim_config(self, stim_config: StimulusConfig):
        """Update the stimulus config with a new config object."""
        if self.stim_config == stim_config:
            return

        self.stim_config = stim_config
        self.stim_generator = StimulusGenerator(self.stim_config)
        self.stim_config_changed.emit()

    def update_protocol_config(self, protocol_config: ProtocolConfig):
        """Update the protocol config with a new config object."""
        if self.protocol_config == protocol_config:
            return

        self.protocol_config = protocol_config
        self.protocol_config_changed.emit()

    def update_filter_config(self, filter_config: FilterConfig):
        """Update the filter config with a new config object."""
        if self.filter_config == filter_config:
            return

        self.filter_config = filter_config
        self.filter_config_changed.emit()

    def get_x_bounds(self):
        t_max = self.stim_generator.config.stim.dur_s

        return (0, t_max)

    def get_y_bounds(self):
        v_min, v_max = self.stim_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
