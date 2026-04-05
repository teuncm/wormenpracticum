import copy

import numpy as np
from app.model.signal import (
    Signal,
    get_time_bounds_s,
    get_time_frame_s,
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
            return -self.amp_v, self.amp_v

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


class StimulusConfig:
    name: str
    n_steps: int
    # Voltage limiting is only applied to samples in the generator.
    limit_v: float
    stim: Stimulus

    def __init__(
        self,
        name: str,
        dur_s: float,
        limit_v: float,
        pulses: list[Pulse],
        n_steps: int = 1,
    ):
        self.name = name
        self.n_steps = n_steps
        self.limit_v = limit_v
        self.stim = Stimulus(dur_s=dur_s, pulses=pulses)


class StimulusGenerator:
    config: StimulusConfig
    stims: list[Stimulus]

    def __init__(self, config: StimulusConfig):
        self.config = config
        self.stims = []
        self._expand()

    def v_bounds(self) -> tuple[float, float]:
        """Voltage bounds of the stimulus generator."""
        v_mins = []
        v_maxs = []
        for stim in self.stims:
            for pulse in stim.pulses:
                v_min, v_max = pulse.v_bounds()
                v_mins.append(v_min)
                v_maxs.append(v_max)

        return min(v_mins), max(v_maxs)

    def t_bounds(self, sr_hz: float) -> tuple[float, float]:
        """Time bounds of the stimulus generator."""
        return self.config.stim.t_bounds(sr_hz=sr_hz)

    def sample_at_idx(
        self, sr_hz: float, stim_idx: int, pulse_idx: int = -1
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sample and clip stimulus or pulse at specified index.
        samples are supplied with timeframe.

        Args:
            sr_hz: Sample rate in Hz.
            stimulus_idx: Index of the stimulus to sample. Must be in [0, n_steps).
            pulse_idx: Index of the pulse to sample. Must be in [-1, n_pulses), where -1 indicates the entire stimulus.

            Returns:
            Tuple of (samples, timeframe_s), where samples is a 1D array of voltage samples, and timeframe_s is a 1D array of time points corresponding to each sample.
        """
        if pulse_idx >= len(self.config.stim.pulses):
            raise ValueError("Pulse index out of range.")
        if stim_idx >= self.config.n_steps:
            raise ValueError("Stimulus index out of range.")

        # Get stimulus at index.
        stim = self.stims[stim_idx]

        if pulse_idx == -1:
            # Sample this stimulus.
            samples_stim = self.clip_samples(stim.sample(sr_hz=sr_hz))
            timeframe_stim = get_time_frame_s(len(samples_stim), sr_hz)

            return samples_stim, timeframe_stim

        # Get pulse at requested index within the stimulus.
        pulse = stim.pulses[pulse_idx]

        # Determine pulse sample offset within this stimulus.
        pulse_offset = quantize_time_point(time_s=pulse.start_s, sr_hz=sr_hz)

        # Sample this pulse.
        samples_pulse = self.clip_samples(pulse.sample(sr_hz=sr_hz))
        timeframe_pulse = get_time_frame_s(
            len(samples_pulse), sr_hz, sample_offset=pulse_offset
        )

        return samples_pulse, timeframe_pulse

    def clip_samples(self, samples: np.ndarray) -> np.ndarray:
        """Clip the samples to the voltage limits set in the stimulus config."""
        return np.clip(samples, -self.config.limit_v, self.config.limit_v)

    def _expand(self) -> None:
        """Expand the stimulus for each step."""
        # Since _step() is in-place, we need to deepcopy the base stimulus to avoid modifying it.
        cur_stim = copy.deepcopy(self.config.stim)
        expanded_stims = []
        for _ in range(self.config.n_steps):
            expanded_stims.append(copy.deepcopy(cur_stim))
            cur_stim._step()

        self.stims = expanded_stims
