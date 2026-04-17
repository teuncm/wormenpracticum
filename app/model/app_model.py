from app.model.stimulus.stimulus_config import DEFAULT_STIMULUS_CONFIG
from app.model.stimulus.stimulus_generator import StimulusGenerator
from PySide6.QtCore import QObject, Signal


class AppModel(QObject):
    stim_generator: StimulusGenerator
    experiment_data = None

    # Signal to emit when stimulus config changed
    stim_config_changed = Signal()

    def __init__(self):
        super().__init__()
        self.init_stim_config()

    def init_stim_config(self):
        self.stim_generator = StimulusGenerator(DEFAULT_STIMULUS_CONFIG)

    def update_stim_config(self, stim_config):
        # If no change was made, return
        if self.stim_generator.config == stim_config:
            return

        self.stim_generator = StimulusGenerator(stim_config)
        self.stim_config_changed.emit()

    def get_x_bounds(self):
        t_max = self.stim_generator.config.stim.dur_s

        return (0, t_max)

    def get_y_bounds(self):
        v_min, v_max = self.stim_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
