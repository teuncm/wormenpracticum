import numpy as np
import scipy as sp
from scipy.signal import butter, sosfiltfilt


def gaussian_filter(sample_rate: float, sigma_seconds: float):
    """Applies a Gaussian filter to the input data."""
    sigma = sigma_seconds * sample_rate

    def filter(data: np.ndarray) -> np.ndarray:
        return sp.ndimage.gaussian_filter(data, sigma=sigma)

    return filter


def lowpass_filter(sample_rate: float, cutoff_hz: float, order: int = 4):
    """Applies a low-pass Butterworth filter to the input data."""
    sos = butter(order, cutoff_hz, btype="low", fs=sample_rate, output="sos")

    def filter(data: np.ndarray) -> np.ndarray:
        return sosfiltfilt(sos, data, axis=-1, padtype=None)  # pyright: ignore[reportArgumentType]

    return filter
