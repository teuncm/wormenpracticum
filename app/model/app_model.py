from app.model.pulse_model import Pulse, PulseGenerator, PulseTrain
from app.model.signal import get_timeframe_s


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

        sr_hz = 1000
        n_samples = self.pulse_generator.width(sr_hz)
        t = get_timeframe_s(n_samples, sr_hz, 0)

        return (t.min(), t.max())

    def get_y_bounds(self):
        if self.pulse_generator is None:
            return None

        sr_hz = 1000
        signal_obj, _ = self.pulse_generator.get_signal(sr_hz, 0)
        y = signal_obj.sample(sr_hz)

        abs_max = max(abs(y.min()), abs(y.max()))

        return (-abs_max, abs_max)
