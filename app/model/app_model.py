from app.model.pulse_model import PulseTrain


class AppModel:
    pulse_config: PulseTrain | None

    def __init__(self):
        self.pulse_config = None

    # def update_pulse_config(self, pulse_data):
    #     pulseSegments = [PulseSegment(**segment) for segment in pulse_data["segments"]]

    #     self.pulse_config = Pulse(pulse_data["N"], pulseSegments)

    # def sample_pulse(self, sample_rate_hz):
    #     if self.pulse_config is None:
    #         return None

    #     return self.pulse_config.sample_pulse(sample_rate_hz)
