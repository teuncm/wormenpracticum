import copy

import numpy as np

import app.feature.stimulus.signal as sgn
from app.feature.stimulus.stimulus import Stimulus
from app.feature.stimulus.stimulus_config import StimulusConfig


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
            timeframe_stim = sgn.get_time_frame_s(len(samples_stim), sr_hz)

            return samples_stim, timeframe_stim

        # Get pulse at requested index within the stimulus.
        pulse = stim.pulses[pulse_idx]

        pulse_start_idx, stim_start_idx, n_overlap = stim.pulse_overlap(pulse, sr_hz)

        # Sample this pulse.
        samples_pulse = self.clip_samples(pulse.sample(sr_hz=sr_hz))
        timeframe_pulse = sgn.get_time_frame_s(
            n_overlap, sr_hz, sample_offset=stim_start_idx
        )

        samples_pulse = samples_pulse[pulse_start_idx : pulse_start_idx + n_overlap]

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
