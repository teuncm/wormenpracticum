import pytest
from app.model.stimulus.pulse import Pulse
from app.model.stimulus.stimulus_config import StimulusConfig
from app.model.stimulus.stimulus_generator import StimulusGenerator

TEST_SR_HZ = 4.0


@pytest.fixture
def gen_basic() -> StimulusGenerator:
    return StimulusGenerator(
        config=StimulusConfig(
            name="basic",
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
