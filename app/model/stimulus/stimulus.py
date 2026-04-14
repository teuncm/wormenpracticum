import app.model.stimulus.signal as sgn
import numpy as np
from app.model.stimulus.pulse import Pulse


class Stimulus(sgn.Signal):
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
        t_min, t_max = sgn.get_time_bounds_s(
            n_samples=n_samples, sr_hz=sr_hz, sample_offset=0
        )

        return t_min, t_max

    def n_samples(self, sr_hz: float) -> int:
        """Get the number of samples in each step of the stimulus config."""
        n_samples = sgn.quantize_time_point(time_s=self.dur_s, sr_hz=sr_hz)

        return max(n_samples, 0)

    def pulse_overlap(self, pulse: Pulse, sr_hz: float):
        """Find where the pulse overlaps with the stimulus in terms of sample indices.
        Return the start index within the pulse, the start index within the stimulus, and the number of samples in the overlap.
        """
        stim_start_idx = 0
        pulse_start_idx = 0
        n_overlap = 0

        stim_lt = 0
        stim_rt = self.n_samples(sr_hz=sr_hz) - 1
        pulse_lt = sgn.quantize_time_point(time_s=pulse.start_s, sr_hz=sr_hz)
        pulse_rt = pulse_lt + pulse.n_samples(sr_hz=sr_hz) - 1

        max_lt = max(pulse_lt, stim_lt)
        min_rt = min(pulse_rt, stim_rt)

        if max_lt <= min_rt:
            n_overlap = min_rt - max_lt + 1

            if pulse_lt < stim_lt:
                stim_start_idx = 0
                pulse_start_idx = stim_lt - pulse_lt
            else:
                stim_start_idx = pulse_lt - stim_lt
                pulse_start_idx = 0
        else:
            n_overlap = 0

        return pulse_start_idx, stim_start_idx, n_overlap

    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the stimulus."""
        # Initialize the sample array.
        n_samples_stim = self.n_samples(sr_hz=sr_hz)
        samples_stim = np.zeros(n_samples_stim)

        # Sample each pulse and add it to the overall stimulus.
        for pulse in self.pulses:
            pulse_start_idx, stim_start_idx, n_overlap = self.pulse_overlap(
                pulse, sr_hz
            )

            # Sample the pulse.
            pulse_samples = pulse.sample(sr_hz=sr_hz)

            samples_stim[stim_start_idx : stim_start_idx + n_overlap] += pulse_samples[
                pulse_start_idx : pulse_start_idx + n_overlap
            ]

        return samples_stim

    def get_latest_pulse_time(self) -> float:
        """Convenience function for pulse creation. Get the latest pulse time as the endpoint of the furthermost pulse."""
        latest_end_time = 0.0

        for pulse in self.pulses:
            pulse_end_time = pulse.start_s + pulse.dur_s
            if pulse_end_time > latest_end_time:
                latest_end_time = pulse_end_time

        return latest_end_time

    def _step(self) -> None:
        """Advance the stimulus state in-place."""
        for pulse in self.pulses:
            pulse._step()

    def __repr__(self) -> str:
        return str(vars(self))
