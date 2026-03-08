import copy

import numpy as np
from app.model.signal import SignalSequence


class Pulse(SignalSequence):
    amp_v: float
    dur_s: float
    step_amp_v: float
    step_dur_s: float
    is_monophasic: bool

    def __init__(
        self, amp_v, dur_s, step_amp_v=0.0, step_dur_s=0.0, is_monophasic=False
    ):
        self.amp_v = amp_v
        self.dur_s = dur_s
        self.step_amp_v = step_amp_v
        self.step_dur_s = step_dur_s
        self.is_monophasic = is_monophasic

    def peak_v(self) -> float:
        """Peak of the pulse."""
        return abs(self.amp_v)

    def actual_dur_s(self, sr_hz) -> float:
        """Total duration of the pulse in seconds, taking into account the actual number of samples."""
        return self.n_samples(sr_hz) / sr_hz

    def n_samples(self, sr_hz) -> int:
        """Number of samples in the pulse."""
        # Guarantee that we can divide the pulse into two parts
        n_half_pulse_samples = int(round(self.dur_s / 2.0 * sr_hz))
        # Guarantee that the number of samples is at least 0
        n_pulse_samples_capped = max(2 * n_half_pulse_samples, 0)

        return n_pulse_samples_capped

    def sample(self, sr_hz) -> np.ndarray:
        """Sample the pulse."""
        n_samples = self.n_samples(sr_hz)

        samples = np.zeros(n_samples)

        # If pulse has no sample, exit early
        if n_samples == 0:
            return samples

        if self.is_monophasic:
            samples[:] = self.amp_v
        else:
            # Allowed because n_samples is guaranteed to be even
            split = n_samples // 2
            samples[:split] = self.amp_v
            samples[split:] = -self.amp_v

        return samples

    def _step(self) -> None:
        """Advance the pulse in-place."""
        self.amp_v += self.step_amp_v
        self.dur_s += self.step_dur_s


class PulseTrain(SignalSequence):
    pulses: list[Pulse]
    n_steps: int

    def __init__(self, pulses, n_steps=1):
        self.pulses = pulses
        self.n_steps = n_steps

    def peak_v(self) -> float:
        """Peak of the train."""
        if not self.pulses:
            return 0.0

        return max(pulse.peak_v() for pulse in self.pulses)

    def actual_dur_s(self, sr_hz) -> float:
        """Total duration of the train in seconds, taking into account the actual number of samples."""
        return sum(pulse.actual_dur_s(sr_hz) for pulse in self.pulses)

    def n_samples(self, sr_hz) -> int:
        """Number of samples in the train."""
        n_samples = sum(pulse.n_samples(sr_hz) for pulse in self.pulses)

        return n_samples

    def sample(self, sr_hz) -> np.ndarray:
        """Sample the train."""
        samples_list = []

        # If pulse list is empty, exit early
        if not self.pulses:
            return np.array([])

        for pulse in self.pulses:
            pulse_samples = pulse.sample(sr_hz)
            samples_list.append(pulse_samples)

        samples = np.concatenate(samples_list)

        return samples

    def _step(self) -> None:
        """Advance the train in-place."""
        for pulse in self.pulses:
            pulse._step()


class PulseGenerator:
    base_train: PulseTrain
    train_steps: list[PulseTrain]

    def __init__(self, base_train: PulseTrain):
        self.base_train = base_train
        self.train_steps = []
        self._expand()

    def width(self, sr_hz) -> int:
        """Width of the train in samples."""
        return self.base_train.n_samples(sr_hz)

    def n_samples(self, sr_hz) -> int:
        """Number of samples in the generated pulse trains."""
        n_samples_per_step = self.width(sr_hz)
        total_n_samples = n_samples_per_step * self.base_train.n_steps

        return total_n_samples

    def get_signal(
        self, sr_hz, train_step_idx, pulse_idx=-1
    ) -> tuple[SignalSequence, int]:
        """Get a specific signal."""
        train = self.train_steps[train_step_idx]

        if pulse_idx == -1:
            return train, 0

        sample_offset = 0
        pulse = train.pulses[pulse_idx]
        for i in range(len(train.pulses)):
            if i == pulse_idx:
                break
            sample_offset += train.pulses[i].n_samples(sr_hz=sr_hz)

        return pulse, sample_offset

    def _expand(self) -> None:
        """Expand the pulse train into a list of pulse trains for each step."""
        cur_train = copy.deepcopy(self.base_train)
        train_steps = []
        for _ in range(self.base_train.n_steps):
            train_steps.append(copy.deepcopy(cur_train))
            cur_train._step()

        self.train_steps = train_steps

    def generate(self, sr_hz) -> np.ndarray:
        """Sample the pulse train over all steps."""
        # Fit all trains to the length of the base train.
        n_samples_per_step = self.base_train.n_samples(sr_hz)

        # Contains pulse train samples for all iterations
        samples_mat = np.zeros((self.base_train.n_steps, n_samples_per_step))

        # Early exit if there is nothing to generate.
        if n_samples_per_step == 0 or self.base_train.n_steps == 0:
            return samples_mat

        for i in range(self.base_train.n_steps):
            cur_samples = self.train_steps[i].sample(sr_hz)
            cur_n_samples = len(cur_samples)

            if cur_n_samples > n_samples_per_step:
                samples_mat[i, :n_samples_per_step] = cur_samples[:n_samples_per_step]
            else:
                samples_mat[i, :cur_n_samples] = cur_samples[:cur_n_samples]

        return samples_mat
