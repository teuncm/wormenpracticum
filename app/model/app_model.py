import pandas as pd
from PySide6.QtCore import QObject, Signal

from app.constants import (
    DEFAULT_FILTER_CONFIG,
    DEFAULT_PROTOCOL_CONFIG,
    DEFAULT_STIMULUS_CONFIG,
)
from app.model.app_state import AppState
from app.model.config.filter_config import FilterConfig
from app.model.config.protocol_config import ProtocolConfig
from app.model.config.stimulus_config import StimulusConfig
from app.model.stimulus.stimulus_generator import StimulusGenerator


class AppModel(QObject):
    """AppModel contains all persistent app data and logic, acting as a single source of truth.
    It emits signals when data changes, allowing views to react and update accordingly."""

    app_state: AppState
    # The stimulus generator instance, created based on the current stimulus config
    stim_generator: StimulusGenerator
    # Filtered experiment data as DataFrame, cached after applying filters to raw data
    # If no filters have been applied, values are the same as raw_data_df
    filtered_data_df: pd.DataFrame | None

    # Emit when any of the configs changed. The changes will be reflected in the view.
    stim_config_changed = Signal()
    protocol_config_changed = Signal()
    filter_config_changed = Signal()

    # Emit when experiment data changed
    experiment_data_changed = Signal()

    def __init__(self):
        super().__init__()
        self.app_state = AppState(
            stim_config=DEFAULT_STIMULUS_CONFIG,
            protocol_config=DEFAULT_PROTOCOL_CONFIG,
            filter_config=DEFAULT_FILTER_CONFIG,
            experiment_config={},
            experiment_metadata={},
            raw_data_df=None,
        )
        self.stim_generator = StimulusGenerator(self.app_state.stim_config)
        self.filtered_data_df = None

    def update_experiment_data(self, df: pd.DataFrame):
        """Update experiment data with a new dataframe."""
        if self.app_state.raw_data_df is not None and self.app_state.raw_data_df.equals(
            df
        ):
            return

        self.app_state.raw_data_df = df
        self.filtered_data_df = df
        self.experiment_data_changed.emit()

    def update_stim_config(self, stim_config: StimulusConfig):
        """Update the stimulus config with a new config object."""
        if self.app_state.stim_config == stim_config:
            return

        self.app_state.stim_config = stim_config
        self.stim_generator = StimulusGenerator(self.app_state.stim_config)
        self.stim_config_changed.emit()

    def update_protocol_config(self, protocol_config: ProtocolConfig):
        """Update the protocol config with a new config object."""
        if self.app_state.protocol_config == protocol_config:
            return

        self.app_state.protocol_config = protocol_config
        self.protocol_config_changed.emit()

    def update_filter_config(self, filter_config: FilterConfig):
        """Update the filter config with a new config object."""
        if self.app_state.filter_config == filter_config:
            return

        self.app_state.filter_config = filter_config
        self.filter_config_changed.emit()

    def get_x_bounds(self):
        t_max = self.stim_generator.config.stim.dur_s

        return (0, t_max)

    def get_y_bounds(self):
        v_min, v_max = self.stim_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
