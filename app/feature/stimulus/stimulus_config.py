from dataclasses import dataclass

from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus import Stimulus


@dataclass
class StimulusConfig:
    """Configuration for the stimulus generator stage."""

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

    def to_dict(self) -> dict:
        return {
            "dur_s": self.stim.dur_s,
            "limit_v": self.limit_v,
            "n_steps": self.n_steps,
            "pulses": [
                {
                    "amp_v": pulse.amp_v,
                    "start_s": pulse.start_s,
                    "dur_s": pulse.dur_s,
                    "step_amp_v": pulse.step_amp_v,
                    "step_start_s": pulse.step_start_s,
                    "step_dur_s": pulse.step_dur_s,
                    "is_monophasic": pulse.is_monophasic,
                }
                for pulse in self.stim.pulses
            ],
        }
