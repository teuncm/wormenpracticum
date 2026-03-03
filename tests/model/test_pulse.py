import numpy as np
import pytest
from app.model.simple_pulse_model import Pulse, PulseGenerator, PulseSegment


@pytest.fixture
def pulse_segment() -> PulseSegment:
    return PulseSegment(amplitude_v=5.0, phase_s=1.0, rest_s=1.5)


@pytest.fixture
def pulse_segment_2() -> PulseSegment:
    return PulseSegment(amplitude_v=4.0, phase_s=1.0, rest_s=0.5)


@pytest.fixture
def pulse(pulse_segment, pulse_segment_2) -> Pulse:
    return Pulse(
        N=2,
        pulse_segments=[
            pulse_segment,
            pulse_segment_2,
        ],
    )


@pytest.fixture
def pulse_generator(pulse) -> PulseGenerator:
    return PulseGenerator(pulse=pulse, sample_rate_hz=2)


def test_timeframe(pulse_generator):
    segment = pulse_generator.pulse.pulse_segments[0]
    samples = segment.sample_segment(sample_rate_hz=2)
    timeframe = pulse_generator.get_timeframe_s(samples, sample_offset=0)

    assert len(timeframe) == len(samples)
    assert timeframe[0] == 0.0
    assert timeframe[-1] == (len(samples) - 1) / 2.0 * 1.0


def test_sample_segment(pulse_segment, pulse_segment_2):
    samples = pulse_segment.sample_segment(sample_rate_hz=2)

    assert np.allclose(samples, [5.0, 5.0, -5.0, -5.0, 0.0, 0.0, 0.0])

    samples_2 = pulse_segment_2.sample_segment(sample_rate_hz=2)

    assert np.allclose(samples_2, [4.0, 4.0, -4.0, -4.0, 0.0])


def test_sample_pulse(pulse):
    samples = pulse.sample_pulse(sample_rate_hz=2)

    expected_samples = np.concatenate(
        [
            np.array([5.0, 5.0, -5.0, -5.0, 0.0, 0.0, 0.0]),
            np.array([4.0, 4.0, -4.0, -4.0, 0.0]),
            np.array([5.0, 5.0, -5.0, -5.0, 0.0, 0.0, 0.0]),
            np.array([4.0, 4.0, -4.0, -4.0, 0.0]),
        ]
    )

    assert np.allclose(samples, expected_samples)
