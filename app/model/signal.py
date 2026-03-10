from abc import ABC, abstractmethod

import numpy as np

MS_PER_S = 1000.0


class SignalSequence(ABC):
    @abstractmethod
    def min_v(self) -> float:
        """Minimum voltage of the signal."""
        pass

    @abstractmethod
    def max_v(self) -> float:
        """Maximum voltage of the signal."""
        pass

    @abstractmethod
    def actual_dur_s(self, sr_hz: float) -> float:
        """Total duration of the signal in seconds, taking into account the actual number of samples."""
        pass

    @abstractmethod
    def n_samples(self, sr_hz: float) -> int:
        """Number of samples in the signal."""
        pass

    @abstractmethod
    def sample(self, sr_hz: float) -> np.ndarray:
        """Sample the signal."""
        pass

    @abstractmethod
    def _step(self) -> None:
        """Advance the signal in-place."""
        pass


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
