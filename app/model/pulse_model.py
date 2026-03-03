# class PulseSegment:
#     V: float
#     PW: float
#     T: float
#     DELTA_V: float
#     DELTA_PW: float
#     DELTA_T: float
#     def __init__(self, V, PW, T, DELTA_V, DELTA_PW, DELTA_T):
#         self.V = V
#         self.PW = PW
#         self.T = T
#         self.DELTA_V = DELTA_V
#         self.DELTA_PW = DELTA_PW
#         self.DELTA_T = DELTA_T
# class Pulse:
#     N: int
#     pulse_segments: list[PulseSegment]
#     def __init__(self, N, pulse_segments):
#         self.N = N
#         self.pulse_segments = pulse_segments
import copy

import numpy as np

MS_PER_S = 1000.0


class PulseSegment:
    amplitude_v: float
    phase_s: float
    rest_s: float
    delta_amplitude_v: float
    delta_phase_s: float
    delta_rest_s: float

    def __init__(
        self,
        amplitude_v,
        phase_s,
        rest_s,
        delta_amplitude_v,
        delta_phase_s,
        delta_rest_s,
    ):
        self.amplitude_v = amplitude_v
        self.phase_s = phase_s
        self.rest_s = rest_s
        self.delta_amplitude_v = delta_amplitude_v
        self.delta_phase_s = delta_phase_s
        self.delta_rest_s = delta_rest_s

    def sample_segment(self, sample_rate_hz):
        num_phase_samples = max(int(round(self.phase_s / 2.0 * sample_rate_hz)), 0)
        num_rest_samples = max(int(round(self.rest_s * sample_rate_hz)), 0)

        print(num_phase_samples)

        pos_phase_samples = np.full(num_phase_samples, self.amplitude_v)
        neg_phase_samples = np.full(num_phase_samples, -self.amplitude_v)
        rest_samples = np.zeros(num_rest_samples)

        return np.concatenate([pos_phase_samples, neg_phase_samples, rest_samples])

    def add_delta(self):
        self.amplitude_v += self.delta_amplitude_v
        self.phase_s += self.delta_phase_s
        self.rest_s += self.delta_rest_s


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
                segment.add_delta()

        return np.concatenate(samples)

    def get_timeframe_s(
        self, samples: np.ndarray, sample_rate_hz: float, sample_offset: int = 0
    ):
        return (np.arange(len(samples)) + sample_offset) / sample_rate_hz


# class PulseGenerator:
#     pulse: Pulse
#     sample_rate_hz: float

#     def __init__(self, pulse: Pulse, sample_rate_hz: float):
#         self.pulse = copy.deepcopy(pulse)
#         self.sample_rate_hz = sample_rate_hz
#         self.cur_sample_idx = 0
#         self.cur_pulse_segment_idx = 0
