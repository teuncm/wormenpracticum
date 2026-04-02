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
            if self.amp_v >= 0:
                return 0, self.amp_v
            else:
                return self.amp_v, 0
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

        n_samples = quantize_time_point(time_s=self.dur_s, sr_hz=sr_hz) + 1

        if not self.is_monophasic:
            # Guarantee that biphasic pulses have an even number of samples
            if n_samples % 2 == 1:
                n_samples += 1

        return n_samples

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
        """Advance the pulse in-place."""
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
        """Get the number of samples in each step of the stimulus preset."""
        n_samples = quantize_time_point(time_s=self.dur_s, sr_hz=sr_hz) + 1

        return n_samples

    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the stimulus."""
        # Initialize the sample array.
        n_samples = self.n_samples(sr_hz=sr_hz)
        samples = np.zeros(n_samples)
        max_idx = n_samples - 1

        # Sample each pulse and add it to the overall stimulus.
        for pulse in self.pulses:
            # Get the pulse's sample offset within the stimulus.
            sample_offset = quantize_time_point(time_s=pulse.start_s, sr_hz=sr_hz)

            # Sample the pulse.
            pulse_samples = pulse.sample(sr_hz=sr_hz)

            # Add the pulse samples to the overall stimulus.
            end_offset = sample_offset + len(pulse_samples)
            if end_offset <= len(samples):
                samples[sample_offset:end_offset] = pulse_samples
            else:
                samples[sample_offset:] = pulse_samples[: max_idx - sample_offset + 1]

        return samples

    def _step(self) -> None:
        """Advance the stimulus in-place."""
        for pulse in self.pulses:
            pulse._step()


class StimulusPreset:
    name: str
    n_steps: int
    stimulus: Stimulus

    def __init__(self, name: str, dur_s: float, pulses: list[Pulse], n_steps: int = 1):
        self.name = name
        self.n_steps = n_steps
        self.stimulus = Stimulus(dur_s=dur_s, pulses=pulses)


class StimulusGenerator:
    preset: StimulusPreset
    stimuli: list[Stimulus]

    def __init__(self, preset: StimulusPreset):
        self.preset = preset
        self.stimuli = []
        self._expand()

    def v_bounds(self) -> tuple[float, float]:
        """Voltage bounds of the stimulus generator."""
        v_mins = []
        v_maxs = []
        for stimulus in self.stimuli:
            for pulse in stimulus.pulses:
                v_min, v_max = pulse.v_bounds()
                v_mins.append(v_min)
                v_maxs.append(v_max)

        return min(v_mins), max(v_maxs)

    def t_bounds(self, sr_hz: float) -> tuple[float, float]:
        """Time bounds of the stimulus generator."""
        n_samples_step = self.preset.stimulus.n_samples(sr_hz=sr_hz)

        t_min, t_max = get_time_bounds_s(
            n_samples=n_samples_step, sr_hz=sr_hz, sample_offset=0
        )

        return t_min, t_max

    def sample_section(
        self, sr_hz: float, stimulus_idx: int, pulse_idx: int = -1
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get a signal at a specific index within the train matrix and its timeframe."""
        if pulse_idx >= len(self.preset.stimulus.pulses):
            raise ValueError("Pulse index out of range.")
        if stimulus_idx >= self.preset.n_steps:
            raise ValueError("Stimulus index out of range.")

        # Get pulse train at requested generator step.
        stimulus = self.stimuli[stimulus_idx]

        if pulse_idx == -1:
            # Sample this train.
            samples = stimulus.sample(sr_hz=sr_hz)
            timeframe = get_time_frame_s(len(samples), sr_hz)

            return samples, timeframe

        # Get pulse at requested index within the train.
        pulse = stimulus.pulses[pulse_idx]

        # Determine pulse sample offset within this particular pulse train.
        sample_offset = quantize_time_point(time_s=pulse.start_s, sr_hz=sr_hz)

        # Sample this pulse.
        samples = pulse.sample(sr_hz=sr_hz)
        timeframe = get_time_frame_s(len(samples), sr_hz, sample_offset=sample_offset)

        return samples, timeframe

    def _expand(self) -> None:
        """Expand the stimulus for each step."""
        # Since _step() is in-place, we need to deepcopy the base stimulus to avoid modifying it.
        cur_stimulus = copy.deepcopy(self.preset.stimulus)
        stimuli = []
        for _ in range(self.preset.n_steps):
            stimuli.append(copy.deepcopy(cur_stimulus))
            cur_stimulus._step()

        self.stimuli = stimuli
