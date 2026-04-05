import numpy as np
from app.model.stimulus.pulse import Pulse
from app.model.stimulus.signal import Signal, get_time_bounds_s, quantize_time_point


class Stimulus(Signal):
    dur_s: float
    pulses: list[Pulse]

    def __init__(self, dur_s: float, pulses: list[Pulse]):
        self.dur_s = dur_s
        self.pulses = pulses

    def v_bounds(self) -> tuple[float, float]:
        """Voltage bounds of the stimulus."""
        v_mins = []
        v_maxs = []
        for pulse in self.pulses:
            v_min, v_max = pulse.v_bounds()
            v_mins.append(v_min)
            v_maxs.append(v_max)

        return min(v_mins), max(v_maxs)

    def t_bounds(self, sr_hz: float) -> tuple[float, float]:
        """Time bounds of the stimulus."""
        n_samples = self.n_samples(sr_hz=sr_hz)
        t_min, t_max = get_time_bounds_s(
            n_samples=n_samples, sr_hz=sr_hz, sample_offset=0
        )

        return t_min, t_max

    def n_samples(self, sr_hz: float) -> int:
        """Get the number of samples in each step of the stimulus config."""
        n_samples = quantize_time_point(time_s=self.dur_s, sr_hz=sr_hz)

        return max(n_samples, 0)

    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the stimulus."""
        # Initialize the sample array.
        n_samples_stim = self.n_samples(sr_hz=sr_hz)
        samples_stim = np.zeros(n_samples_stim)

        # Sample each pulse and add it to the overall stimulus.
        for pulse in self.pulses:
            # Get the pulse's sample offset within the stimulus.
            pulse_offset = quantize_time_point(time_s=pulse.start_s, sr_hz=sr_hz)
            n_samples_pulse = pulse.n_samples(sr_hz=sr_hz)
            n_samples_pulse_truncated = min(
                n_samples_pulse, n_samples_stim - pulse_offset
            )

            # Sample the pulse.
            pulse_samples = pulse.sample(sr_hz=sr_hz)

            samples_stim[pulse_offset : pulse_offset + n_samples_pulse_truncated] = (
                pulse_samples[:n_samples_pulse_truncated]
            )

        return samples_stim

    def _step(self) -> None:
        """Advance the stimulus state in-place."""
        for pulse in self.pulses:
            pulse._step()

    def __repr__(self) -> str:
        return str(vars(self))
