from app.model.pulse import Pulse, PulseGenerator, PulseTrain

PULSE_SAMPLE_HZ = 1000


class AppModel:
    pulse_config: PulseTrain | None
    pulse_generator: PulseGenerator | None

    def __init__(self):
        self.pulse_config = None
        self.pulse_generator = None

    def update_pulse_config(self, pulse_data):
        pulses = [Pulse(**segment) for segment in pulse_data["segments"]]
        train = PulseTrain(pulses, n_steps=pulse_data["N"])
        generator = PulseGenerator(train)

        self.pulse_config = train
        self.pulse_generator = generator

    def get_x_bounds(self):
        if self.pulse_generator is None:
            return None

        dur_s = self.pulse_generator.base_train.actual_dur_s(sr_hz=PULSE_SAMPLE_HZ)

        return (0, dur_s)

    def get_y_bounds(self):
        if self.pulse_generator is None:
            return None

        peak = self.pulse_generator.base_train.peak_v()

        return (-peak, peak)
