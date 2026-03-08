from abc import ABC, abstractmethod

import numpy as np

MS_PER_S = 1000.0


class SignalSequence(ABC):
    @abstractmethod
    def peak_v(self) -> float:
        """Peak of the signal."""
        pass

    @abstractmethod
    def actual_dur_s(self, sr_hz) -> float:
        """Total duration of the signal in seconds, taking into account the actual number of samples."""
        pass

    @abstractmethod
    def n_samples(self, sr_hz) -> int:
        """Number of samples in the signal."""
        pass

    @abstractmethod
    def sample(self, sr_hz) -> np.ndarray:
        """Sample the signal."""
        pass

    @abstractmethod
    def _step(self) -> None:
        """Advance the signal in-place."""
        pass


def get_timeframe_s(n_samples: int, sr_hz: float, sample_offset: int = 0) -> np.ndarray:
    """Get signal timeframe using the given sample rate and sample offset."""
    timeframe = (np.arange(n_samples) + sample_offset) / sr_hz

    return timeframe
