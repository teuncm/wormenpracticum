import pytest

from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus import Stimulus

TEST_SR_HZ = 4.0


def test_empty_stimulus_has_zero_voltage():
    stimulus = Stimulus(dur_s=2.0, pulses=[])

    assert stimulus.v_bounds() == (0.0, 0.0)
    assert stimulus.sample(TEST_SR_HZ).tolist() == [0.0] * 8


@pytest.fixture
def stimulus_basic() -> Stimulus:
    return Stimulus(
        dur_s=2.0,
        pulses=[
            Pulse(
                amp_v=1.0,
                start_s=0.0,
                dur_s=1.0,
            ),
            Pulse(
                amp_v=2.0,
                start_s=0.75,
                dur_s=0.5,
                is_monophasic=True,
            ),
            Pulse(
                amp_v=-1.0,
                start_s=1.5,
                dur_s=1.0,
                is_monophasic=True,
            ),
            Pulse(
                amp_v=-1.0,
                start_s=42.0,
                dur_s=1.0,
                is_monophasic=True,
            ),
        ],
    )


def test_stim(stimulus_basic: Stimulus) -> None:
    assert len(stimulus_basic.pulses) == 4

    assert stimulus_basic.sample(sr_hz=TEST_SR_HZ).tolist() == [
        1.0,
        1.0,
        -1.0,
        2.0,
        2.0,
        0.0,
        -1.0,
        -1.0,
    ]
