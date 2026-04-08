import numpy as np
from app.model.stimulus.signal import (
    Signal,
    get_time_bounds_s,
    quantize_time_point,
)


class Pulse(Signal):
    amp_v: float
    start_s: float
    dur_s: float
    step_amp_v: float
    step_start_s: float
    step_dur_s: float
    is_monophasic: bool

    def __init__(
        self,
        amp_v,
        start_s,
        dur_s,
        step_amp_v=0.0,
        step_start_s=0.0,
        step_dur_s=0.0,
        is_monophasic=False,
    ):
        self.amp_v = amp_v
        self.start_s = start_s
        self.dur_s = dur_s
        self.step_amp_v = step_amp_v
        self.step_start_s = step_start_s
        self.step_dur_s = step_dur_s
        self.is_monophasic = is_monophasic

    def v_bounds(self) -> tuple[float, float]:
        """Voltage bounds of the pulse."""
        if self.is_monophasic:
            return self.amp_v, self.amp_v
        else:
            return -abs(self.amp_v), abs(self.amp_v)

    def t_bounds(self, sr_hz: float) -> tuple[float, float]:
        """Time bounds of the quantized pulse."""
        sample_offset = quantize_time_point(time_s=self.start_s, sr_hz=sr_hz)
        n_samples = self.n_samples(sr_hz=sr_hz)

        t_min, t_max = get_time_bounds_s(
            n_samples=n_samples, sr_hz=sr_hz, sample_offset=sample_offset
        )

        return t_min, t_max

    def n_samples(self, sr_hz: float) -> int:
        """Number of samples in the pulse."""
        # Early exit
        if self.dur_s <= 0:
            return 0

        n_samples = quantize_time_point(time_s=self.dur_s, sr_hz=sr_hz)

        if not self.is_monophasic:
            # Guarantee that biphasic pulses have an even number of samples.
            # Causes truncation by at most one extra sample.
            if n_samples % 2 == 1:
                n_samples -= 1

        return max(n_samples, 0)

    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the pulse."""
        n_samples = self.n_samples(sr_hz)

        samples = np.zeros(n_samples)

        # If pulse has no sample, exit early
        if n_samples == 0:
            return samples

        if self.is_monophasic:
            samples[:] = self.amp_v
        else:
            # Allowed because n_samples is guaranteed to be even for biphasic pulses.
            split = n_samples // 2
            samples[:split] = self.amp_v
            samples[split:] = -self.amp_v

        return samples

    def _step(self) -> None:
        """Advance the pulse state in-place."""
        self.amp_v += self.step_amp_v
        self.start_s += self.step_start_s
        self.dur_s += self.step_dur_s

    def __repr__(self) -> str:
        return str(vars(self))
