from app.model.stimulus.pulse import Pulse
from app.model.stimulus.stimulus_config import StimulusConfig
from app.model.stimulus.stimulus_generator import StimulusGenerator
from PySide6.QtCore import QObject, Signal


class AppModel(QObject):
    # To do: add default generator
    stimulus_generator: StimulusGenerator | None
    # To do: implement experiment protocol
    protocol: None

    # Signal to emit when stimulus config changed
    stim_config_changed = Signal()

    def __init__(self):
        super().__init__()
        self.stimulus_generator = None
        self.protocol = None

    def update_stim_config(self, stim_form_data):
        pulses = [Pulse(**segment) for segment in stim_form_data["segments"]]
        stim_config = StimulusConfig(
            pulses=pulses,
            n_steps=stim_form_data["N"],
            dur_s=stim_form_data["dur_s"],
            limit_v=stim_form_data["limit_v"],
        )
        stim_generator = StimulusGenerator(stim_config)

        self.stimulus_generator = stim_generator
        self.stim_config_changed.emit()

    def get_x_bounds(self):
        if self.stimulus_generator is None:
            return None

        t_max = self.stimulus_generator.config.stim.dur_s

        return (0, t_max)

    def get_y_bounds(self):
        if self.stimulus_generator is None:
            return None

        v_min, v_max = self.stimulus_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
