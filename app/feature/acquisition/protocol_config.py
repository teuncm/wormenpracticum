from dataclasses import dataclass


@dataclass
class ProtocolConfig:
    """Configuration for the protocol stage."""

    positive_channel: int
    negative_channel: int
    selected_pins: list[int]
    sample_rate_divider: int

    def __init__(
        self,
        positive_channel: int,
        negative_channel: int,
        selected_pins: list[int],
        sample_rate_divider: int = 1,
    ):
        self.positive_channel = positive_channel
        self.negative_channel = negative_channel
        self.selected_pins = selected_pins
        self.sample_rate_divider = sample_rate_divider
