import pytest
from app.model.pulse import Pulse, StimulusConfig, StimulusGenerator

TEST_SR_HZ = 4.0


@pytest.fixture
def stimulus_basic() -> StimulusGenerator:
    return StimulusGenerator(
        config=StimulusConfig(
            name="basic",
            dur_s=2.0,
            limit_v=1.0,
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
            ],
            n_steps=2,
        )
    )
