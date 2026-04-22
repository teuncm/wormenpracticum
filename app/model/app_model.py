import pandas as pd
from app.model.stimulus.stimulus_config import DEFAULT_STIMULUS_CONFIG, StimulusConfig
from app.model.stimulus.stimulus_generator import StimulusGenerator
from PySide6.QtCore import QObject, Signal


class AppModel(QObject):
    """AppModel contains all persistent app data and logic, acting as a single source of truth.
    It emits signals when data changes, allowing views to react and update accordingly."""

    # Configuration for the stimulus generator
    stim_config: StimulusConfig
    # The stimulus generator instance, created based on the current stimulus config
    stim_generator: StimulusGenerator
    # Experimental configuration
    experiment_config: dict
    # Experiment metadata
    experiment_metadata: dict
    # Raw experiment data as DataFrame
    raw_data_df: pd.DataFrame | None
    # Filtered experiment data as DataFrame, cached after applying filters to raw data
    # If no filters have been applied, values are the same as raw_data_df
    filtered_data_df: pd.DataFrame | None

    # Emit when stimulus config changed
    stim_config_changed = Signal()

    # Emit when experiment data changed
    experiment_data_changed = Signal()

    def __init__(self):
        super().__init__()
        self.init_props()

    def init_props(self):
        self.stim_config = DEFAULT_STIMULUS_CONFIG
        self.stim_generator = StimulusGenerator(self.stim_config)
        self.experiment_config = {}
        self.experiment_metadata = {}
        self.raw_data_df = None
        self.filtered_data_df = None

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

    def get_x_bounds(self):
        t_max = self.stim_generator.config.stim.dur_s

        return (0, t_max)

    def get_y_bounds(self):
        v_min, v_max = self.stim_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
