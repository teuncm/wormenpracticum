from app.model.stimulus.pulse import Pulse
from app.model.stimulus.stimulus_config import StimulusConfig
from app.model.stimulus.stimulus_generator import StimulusGenerator

DEFAULT_LIMIT_V = 1.5


class AppModel:
    # To do: add default generator
    stimulus_generator: StimulusGenerator | None
    # To do: implement experiment protocol
    protocol: None

    def __init__(self):
        self.stimulus_generator = None
        self.protocol = None

    def update_pulse_config(self, stim_form_data):
        pulses = [Pulse(**segment) for segment in stim_form_data["segments"]]
        stim_config = StimulusConfig(
            pulses=pulses,
            n_steps=stim_form_data["N"],
            name=stim_form_data.get("name", "Custom Stimulus") or "Custom Stimulus",
            dur_s=stim_form_data.get("dur_s", 3.0),
            limit_v=stim_form_data.get("limit_v", DEFAULT_LIMIT_V),
        )
        stim_generator = StimulusGenerator(stim_config)

        self.stimulus_generator = stim_generator

    def get_x_bounds(self):
        if self.stimulus_generator is None:
            return None

        t_min, t_max = self.stimulus_generator.t_bounds(sr_hz=1000)

        return (t_min, t_max)

    def get_y_bounds(self):
        if self.stimulus_generator is None:
            return None

        v_min, v_max = self.stimulus_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
