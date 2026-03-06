import numpy as np
import pytest
from app.model.pulse_model import Pulse, PulseGenerator, PulseTrain

TEST_SR = 2.0


@pytest.fixture
def gen_pulse() -> Pulse:
    return Pulse(amp_v=7.0, dur_s=2, step_amp_v=1, step_dur_s=-1)


@pytest.fixture
def gen_pulse_2() -> Pulse:
    return Pulse(amp_v=-2, dur_s=1, step_amp_v=0, step_dur_s=0, is_monophasic=True)


@pytest.fixture
def gen_pulse_3() -> Pulse:
    return Pulse(amp_v=67, dur_s=0, step_amp_v=0, step_dur_s=67, is_monophasic=True)


@pytest.fixture
def get_train_decreasing(gen_pulse, gen_pulse_2) -> PulseTrain:
    return PulseTrain(pulses=[gen_pulse, gen_pulse_2], n_steps=2)


@pytest.fixture
def get_train_increasing(gen_pulse, gen_pulse_3) -> PulseTrain:
    return PulseTrain(pulses=[gen_pulse, gen_pulse_3], n_steps=2)


def test_pulse_sample(gen_pulse):
    """Verify that pulse sampling produces the expected samples."""
    samples = gen_pulse.sample(sr_hz=TEST_SR)

    assert np.allclose(samples, np.array([7.0, 7.0, -7.0, -7.0]))


def test_train_sample(get_train_decreasing):
    """Verify that train sampling produces the expected samples."""
    samples = get_train_decreasing.sample(sr_hz=TEST_SR)

    assert np.allclose(samples, np.array([7.0, 7.0, -7.0, -7.0, -2, -2]))


def test_generator_sample(get_train_decreasing, get_train_increasing):
    """Verify that generator sampling produces the expected samples."""
    samples = PulseGenerator(get_train_decreasing).generate(sr_hz=TEST_SR)
    expected_samples = np.array(
        [[7.0, 7.0, -7.0, -7.0, -2, -2], [8.0, -8.0, -2, -2, 0, 0]]
    )

    assert np.allclose(samples, expected_samples)

    samples = PulseGenerator(get_train_increasing).generate(sr_hz=TEST_SR)
    expected_samples = np.array([[7.0, 7.0, -7.0, -7.0], [8.0, -8.0, 67, 67]])

    assert np.allclose(samples, expected_samples)
