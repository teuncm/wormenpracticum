from app.model.stimulus.pulse import Pulse, PulseGenerator, PulseTrain


class AppModel:
    # To do: add default generator
    pulse_generator: PulseGenerator | None
    # To do: implement experiment protocol
    protocol: None

    def __init__(self):
        self.pulse_generator = None
        self.protocol = None

    def update_pulse_config(self, pulse_data):
        pulses = [Pulse(**segment) for segment in pulse_data["segments"]]
        train = PulseTrain(pulses, n_steps=pulse_data["N"])
        generator = PulseGenerator(train)

        self.pulse_generator = generator

    def get_x_bounds(self):
        if self.pulse_generator is None:
            return None

        t_max = self.pulse_generator.target_dur_s()

        return (0, t_max)

    def get_y_bounds(self):
        if self.pulse_generator is None:
            return None

        v_min, v_max = self.pulse_generator.v_bounds()
        v_peak = max(abs(v_min), abs(v_max))

        return (-v_peak, v_peak)
