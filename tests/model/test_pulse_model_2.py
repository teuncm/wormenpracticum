import pytest
from app.model.pulse_model_2 import Pulse, PulseGenerator, PulseTrain


@pytest.fixture
def gen_pulse() -> Pulse:
    return Pulse(amp_v=1.0, dur_s=0.01, step_amp_v=0.5, step_dur_s=0.005)


@pytest.fixture
def gen_pulse_2() -> Pulse:
    return Pulse(amp_v=0.5, dur_s=0.02, step_amp_v=0.25, step_dur_s=0.01)


@pytest.fixture
def get_train() -> PulseTrain:
    pulse = gen_pulse()
    pulse_2 = gen_pulse_2()
    return PulseTrain(pulses=[pulse, pulse_2], n_steps=3)


@pytest.fixture
def get_generator() -> PulseGenerator:
    base_train = get_train()
    return PulseGenerator(base_train=base_train, sr_hz=2)
