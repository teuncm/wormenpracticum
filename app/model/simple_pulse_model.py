import copy

import numpy as np


class PulseSegment:
    amplitude_v: float
    phase_s: float
    rest_s: float

    def __init__(self, amplitude_v, phase_s, rest_s):
        self.amplitude_v = amplitude_v
        self.phase_s = phase_s
        self.rest_s = rest_s

    def sample_segment(self, sample_rate_hz):
        num_phase_samples = int(round(self.phase_s * sample_rate_hz))
        num_rest_samples = int(round(self.rest_s * sample_rate_hz))

        pos_phase_samples = np.full(num_phase_samples, self.amplitude_v)
        neg_phase_samples = np.full(num_phase_samples, -self.amplitude_v)
        rest_samples = np.zeros(num_rest_samples)

        return np.concatenate([pos_phase_samples, neg_phase_samples, rest_samples])


class Pulse:
    N: int
    pulse_segments: list[PulseSegment]

    def __init__(self, N, pulse_segments):
        self.N = N
        self.pulse_segments = pulse_segments

    def sample_pulse(self, sample_rate_hz):
        samples = []

        for _ in range(self.N):
            for segment in self.pulse_segments:
                samples.append(segment.sample_segment(sample_rate_hz))

        return np.concatenate(samples)


class PulseGenerator:
    pulse: Pulse
    sample_rate_hz: float

    def __init__(self, pulse: Pulse, sample_rate_hz: float):
        self.pulse = copy.deepcopy(pulse)
        self.sample_rate_hz = sample_rate_hz

    def get_timeframe_s(self, samples: np.ndarray, sample_offset: int = 0):
        return (np.arange(len(samples)) + sample_offset) / self.sample_rate_hz
