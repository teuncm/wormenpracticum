import numpy as np
import pytest
from app.model.pulse import Pulse, PulseGenerator, PulseTrain

TEST_SR_HZ = 4.0


@pytest.fixture
def neg_step_dur_pulse() -> Pulse:
    return Pulse(amp_v=7.0, dur_s=1, step_amp_v=1, step_dur_s=-0.5)


@pytest.fixture
def zero_step_dur_pulse() -> Pulse:
    return Pulse(amp_v=-2, dur_s=0.5, step_amp_v=0, step_dur_s=0, is_monophasic=True)


@pytest.fixture
def pos_step_dur_pulse() -> Pulse:
    return Pulse(amp_v=5, dur_s=0, step_amp_v=0, step_dur_s=0.5, is_monophasic=True)


@pytest.fixture
def overflow_step_dur_pulse() -> Pulse:
    return Pulse(amp_v=67, dur_s=0, step_amp_v=0, step_dur_s=67, is_monophasic=True)


@pytest.fixture
def get_train_decreasing(neg_step_dur_pulse, zero_step_dur_pulse) -> PulseTrain:
    return PulseTrain(pulses=[neg_step_dur_pulse, zero_step_dur_pulse], n_steps=2)


@pytest.fixture
def get_train_equal(neg_step_dur_pulse, pos_step_dur_pulse) -> PulseTrain:
    return PulseTrain(pulses=[neg_step_dur_pulse, pos_step_dur_pulse], n_steps=2)


@pytest.fixture
def get_train_overflow(neg_step_dur_pulse, overflow_step_dur_pulse) -> PulseTrain:
    return PulseTrain(pulses=[neg_step_dur_pulse, overflow_step_dur_pulse], n_steps=2)


def test_pulse_sample(neg_step_dur_pulse):
    """Verify that pulse sampling produces the expected samples."""
    samples = neg_step_dur_pulse.sample(sr_hz=TEST_SR_HZ)

    assert np.allclose(samples, np.array([7.0, 7.0, -7.0, -7.0]))


def test_train_sample(get_train_decreasing):
    """Verify that train sampling produces the expected samples."""
    samples = get_train_decreasing.sample(sr_hz=TEST_SR_HZ)

    assert np.allclose(samples, np.array([7.0, 7.0, -7.0, -7.0, -2, -2]))


def test_generator_sample(get_train_decreasing, get_train_equal, get_train_overflow):
    """Verify that generator sampling produces the expected samples."""
    samples = PulseGenerator(get_train_decreasing).sample_mat(sr_hz=TEST_SR_HZ)
    expected_samples = np.array(
        [[7.0, 7.0, -7.0, -7.0, -2, -2], [8.0, -8.0, -2, -2, 0, 0]]
    )

    assert np.allclose(samples, expected_samples)

    samples = PulseGenerator(get_train_equal).sample_mat(sr_hz=TEST_SR_HZ)
    expected_samples = np.array([[7.0, 7.0, -7.0, -7.0], [8.0, -8.0, 5, 5]])

    assert np.allclose(samples, expected_samples)

    samples = PulseGenerator(get_train_overflow).sample_mat(sr_hz=TEST_SR_HZ)
    expected_samples = np.array([[7.0, 7.0, -7.0, -7.0], [8.0, -8.0, 67, 67]])

    assert np.allclose(samples, expected_samples)


@pytest.fixture
def round_down_dur_neg_v_pulse() -> Pulse:
    return Pulse(amp_v=-5.0, dur_s=0.7, step_amp_v=0, step_dur_s=0)


@pytest.fixture
def round_up_dur_neg_v_pulse() -> Pulse:
    return Pulse(amp_v=-5.0, dur_s=0.8, step_amp_v=0, step_dur_s=0)


def test_peak(round_down_dur_neg_v_pulse):
    """Verify that peak calculations are correct."""
    pulse = round_down_dur_neg_v_pulse
    assert pulse.peak_v() == 5.0

    train = PulseTrain(pulses=[pulse], n_steps=1)
    assert train.peak_v() == 5.0


def test_duration_round_down(round_down_dur_neg_v_pulse):
    """Verify that downwards duration rounding works."""
    pulse = round_down_dur_neg_v_pulse
    assert pulse.actual_dur_s(sr_hz=TEST_SR_HZ) == 0.5

    train = PulseTrain(pulses=[pulse], n_steps=1)
    assert train.actual_dur_s(sr_hz=TEST_SR_HZ) == 0.5


def test_duration_round_up(round_up_dur_neg_v_pulse):
    """Verify that upwards duration rounding works."""
    pulse = round_up_dur_neg_v_pulse
    assert pulse.actual_dur_s(sr_hz=TEST_SR_HZ) == 1.0

    train = PulseTrain(pulses=[pulse], n_steps=1)
    assert train.actual_dur_s(sr_hz=TEST_SR_HZ) == 1.0


def test_n_samples(round_down_dur_neg_v_pulse):
    """Verify that n_samples calculations are correct."""
    pulse = round_down_dur_neg_v_pulse
    assert pulse.n_samples(sr_hz=TEST_SR_HZ) == 2
    assert pulse.sample(sr_hz=TEST_SR_HZ).shape[0] == 2

    train = PulseTrain(pulses=[pulse, pulse], n_steps=1)
    assert train.n_samples(sr_hz=TEST_SR_HZ) == 4
    assert train.sample(sr_hz=TEST_SR_HZ).shape[0] == 4


@pytest.fixture
def monophasic_pulse() -> Pulse:
    return Pulse(amp_v=5, dur_s=2, step_amp_v=0, step_dur_s=0, is_monophasic=True)


def test_zero_sum(round_up_dur_neg_v_pulse, monophasic_pulse):
    """Test that all sampled pulses sum to zero."""
    pulse = round_up_dur_neg_v_pulse
    samples = pulse.sample(sr_hz=TEST_SR_HZ)
    assert np.isclose(np.sum(samples), 0.0)

    train = PulseTrain(pulses=[pulse, pulse], n_steps=1)
    samples = train.sample(sr_hz=TEST_SR_HZ)
    assert np.isclose(np.sum(samples), 0.0)


def test_monophasic_sample(monophasic_pulse):
    """Verify that monophasic pulse sampling produces the expected samples."""
    pulse = monophasic_pulse
    train = PulseTrain(pulses=[pulse], n_steps=2)
    generator = PulseGenerator(train)
    samples = generator.sample_mat(sr_hz=TEST_SR_HZ)

    assert np.isclose(np.sum(samples), 5 * 2 * 2 * TEST_SR_HZ)
    assert np.allclose(samples.flatten(), [5.0] * 16)
