import numpy as np
import pytest
from app.model.stimulus.pulse import Pulse

TEST_SR_HZ = 4.0


@pytest.fixture
def pulse_basic() -> Pulse:
    return Pulse(
        amp_v=1.0,
        start_s=0.6,
        dur_s=0.8,
    )


@pytest.fixture
def pulse_basic_monophasic() -> Pulse:
    return Pulse(
        amp_v=-1.0,
        start_s=0.6,
        dur_s=0.8,
        is_monophasic=True,
    )


def test_v_bounds(pulse_basic: Pulse) -> None:
    v_min, v_max = pulse_basic.v_bounds()
    sampler = pulse_basic.sample(sr_hz=TEST_SR_HZ)

    assert v_min == -1.0 == np.min(sampler)
    assert v_max == 1.0 == np.max(sampler)


def test_v_bounds_monophasic(pulse_basic_monophasic: Pulse) -> None:
    v_min, v_max = pulse_basic_monophasic.v_bounds()
    sampler = pulse_basic_monophasic.sample(sr_hz=TEST_SR_HZ)

    assert v_min == -1.0 == np.min(sampler)
    assert v_max == -1.0 == np.max(sampler)


def test_n_samples(pulse_basic: Pulse) -> None:
    assert pulse_basic.n_samples(sr_hz=TEST_SR_HZ) == 2


def test_n_samples_monophasic(pulse_basic_monophasic: Pulse) -> None:
    assert pulse_basic_monophasic.n_samples(sr_hz=TEST_SR_HZ) == 3


def test_t_bounds(pulse_basic: Pulse) -> None:
    assert pulse_basic.t_bounds(sr_hz=TEST_SR_HZ) == (0.5, 1.0)


def test_t_bounds_monophasic(pulse_basic_monophasic: Pulse) -> None:
    assert pulse_basic_monophasic.t_bounds(sr_hz=TEST_SR_HZ) == (0.5, 1.25)
