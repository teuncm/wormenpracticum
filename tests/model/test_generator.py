import numpy as np
import pytest

from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator

TEST_SR_HZ = 4.0


def test_generator_without_pulses_has_zero_voltage():
    generator = StimulusGenerator(StimulusConfig(2.0, 3.0, [], n_steps=2))

    assert generator.v_bounds() == (0.0, 0.0)
    for step in range(2):
        samples, times = generator.sample_at_idx(TEST_SR_HZ, step)
        np.testing.assert_array_equal(samples, np.zeros(8))
        np.testing.assert_array_equal(times, np.arange(8) / TEST_SR_HZ)


@pytest.fixture
def gen_basic() -> StimulusGenerator:
    return StimulusGenerator(
        config=StimulusConfig(
            dur_s=2.0,
            limit_v=3.0,
            pulses=[
                Pulse(
                    amp_v=1.0, start_s=0.0, dur_s=1.0, step_amp_v=-0.5, step_dur_s=0.5
                ),
                Pulse(
                    amp_v=2.0,
                    start_s=1.5,
                    dur_s=0.5,
                    step_dur_s=-1.0,
                    is_monophasic=True,
                ),
            ],
            n_steps=2,
        )
    )


def test_stimulus_generator(gen_basic: StimulusGenerator) -> None:
    stim, _ = gen_basic.sample_at_idx(sr_hz=TEST_SR_HZ, stim_idx=0)

    assert stim.tolist() == [1.0, 1.0, -1, -1, 0.0, 0.0, 2.0, 2.0]

    stim2, _ = gen_basic.sample_at_idx(sr_hz=TEST_SR_HZ, stim_idx=1)

    assert stim2.tolist() == [0.5, 0.5, 0.5, -0.5, -0.5, -0.5, 0, 0]


@pytest.mark.parametrize("n_steps", [1, 10])
def test_sample_all_preserves_steps_and_clipping(n_steps):
    generator = StimulusGenerator(
        StimulusConfig(
            dur_s=1.0,
            limit_v=3.0,
            pulses=[
                Pulse(
                    amp_v=1.0,
                    start_s=0.0,
                    dur_s=0.5,
                    step_amp_v=0.5,
                    is_monophasic=True,
                )
            ],
            n_steps=n_steps,
        )
    )

    samples, times = generator.sample_all(TEST_SR_HZ)

    expected = []
    for step in range(n_steps):
        expected.extend([min(1.0 + step * 0.5, 3.0)] * 2 + [0.0] * 2)
    np.testing.assert_array_equal(samples, expected)
    np.testing.assert_array_equal(times, np.arange(4 * n_steps) / TEST_SR_HZ)


def test_sample_all_requires_stimuli():
    generator = StimulusGenerator(StimulusConfig(1.0, 3.0, [], n_steps=0))
    with pytest.raises(ValueError, match="At least one stimulus"):
        generator.sample_all(TEST_SR_HZ)
