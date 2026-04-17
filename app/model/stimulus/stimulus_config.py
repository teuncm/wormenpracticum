from dataclasses import dataclass

from app.model.stimulus.pulse import Pulse
from app.model.stimulus.stimulus import Stimulus


@dataclass
class StimulusConfig:
    n_steps: int
    # Voltage limiting is only applied to samples in the generator.
    limit_v: float
    stim: Stimulus

    def __init__(
        self,
        dur_s: float,
        limit_v: float,
        pulses: list[Pulse],
        n_steps: int = 1,
    ):
        self.n_steps = n_steps
        self.limit_v = limit_v
        self.stim = Stimulus(dur_s=dur_s, pulses=pulses)


DEFAULT_STIMULUS_CONFIG = StimulusConfig(
    dur_s=0.01,
    limit_v=1.5,
    pulses=[
        Pulse(
            amp_v=0.5,
            start_s=0.001,
            dur_s=0.002,
        )
    ],
)
