from app.model.stimulus.pulse import Pulse
from app.model.stimulus.stimulus import Stimulus


class StimulusConfig:
    name: str
    n_steps: int
    # Voltage limiting is only applied to samples in the generator.
    limit_v: float
    stim: Stimulus

    def __init__(
        self,
        name: str,
        dur_s: float,
        limit_v: float,
        pulses: list[Pulse],
        n_steps: int = 1,
    ):
        self.name = name
        self.n_steps = n_steps
        self.limit_v = limit_v
        self.stim = Stimulus(dur_s=dur_s, pulses=pulses)


DEFAULT_STIMULUS_CONFIG = StimulusConfig(
    name="Default Stimulus",
    dur_s=3.0,
    limit_v=1.0,
    pulses=[
        Pulse(
            amp_v=1.0,
            start_s=0.5,
            dur_s=0.5,
        )
    ],
)
