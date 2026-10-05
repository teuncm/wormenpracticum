from dataclasses import dataclass

SAMPLE_RATE_DIVIDERS = tuple(2**power for power in range(11))


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
        # Keep older saved dividers within the supported powers of two.
        self.sample_rate_divider = next(
            (
                divider
                for divider in SAMPLE_RATE_DIVIDERS
                if divider >= sample_rate_divider
            ),
            SAMPLE_RATE_DIVIDERS[-1],
        )
