import math
from abc import ABC, abstractmethod

import numpy as np

MV_PER_V = 1000.0
MS_PER_S = 1000.0


class Signal(ABC):
    @abstractmethod
    def v_bounds(self) -> tuple[float, float]:
        """Voltage bounds of the signal."""
        pass

    @abstractmethod
    def t_bounds(self, sr_hz: float) -> tuple[float, float]:
        """Time bounds of the signal."""
        pass

    @abstractmethod
    def n_samples(self, sr_hz: float) -> int:
        """Number of samples in the signal."""
        pass

    @abstractmethod
    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the signal at the given sample rate."""
        pass


def quantize_time_point(time_s: float, sr_hz: float) -> int:
    """Quantize a time point to a sample offset."""
    sample_offset = int(math.floor(time_s * sr_hz))

    return sample_offset


def get_time_frame_s(
    n_samples: int, sr_hz: float, sample_offset: int = 0
) -> np.ndarray:
    """Get sample timeframe using the given sample rate and sample offset."""
    timeframe = (np.arange(n_samples) + sample_offset) / sr_hz

    return timeframe


def get_time_point_s(sr_hz: float, sample_offset: int) -> float:
    """Get sample timepoint using the given sample rate and sample offset."""
    timepoint = sample_offset / sr_hz

    return timepoint


def get_time_bounds_s(
    n_samples: int, sr_hz: float, sample_offset: int = 0
) -> tuple[float, float]:
    """Get sample time bounds using the given sample rate and sample offset."""
    left = get_time_point_s(sr_hz=sr_hz, sample_offset=sample_offset)
    right = get_time_point_s(sr_hz=sr_hz, sample_offset=sample_offset + n_samples)

    return left, right
