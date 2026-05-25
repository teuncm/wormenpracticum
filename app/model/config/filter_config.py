from dataclasses import dataclass


@dataclass
class FilterConfig:
    """Configuration for the filter stage."""

    low_pass_cutoff_hz: float
    suppress_50hz: bool
    remove_dc_offset: bool

    def __init__(
        self,
        low_pass_cutoff_hz: float,
        suppress_50hz: bool,
        remove_dc_offset: bool = True,
    ):
        self.low_pass_cutoff_hz = low_pass_cutoff_hz
        self.suppress_50hz = suppress_50hz
        self.remove_dc_offset = remove_dc_offset
