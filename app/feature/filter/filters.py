import numpy as np
import pandas as pd
import scipy as sp
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos

from app.feature.filter.filter_config import FilterConfig
from app.shared.recording_metadata import validate_sample_rate


def filter_recording(
    raw: pd.DataFrame, config: FilterConfig, sample_rate_hz: float | None
) -> pd.DataFrame:
    """Filter voltage channels while preserving timestamps and missing samples."""
    channels = [column for column in raw if column != "t_(s)"]
    if not channels:
        raise ValueError("The recording has no voltage channels.")

    stages = []
    if config.low_pass_cutoff_hz or config.suppress_50hz:
        sample_rate_hz = recording_sample_rate(raw, sample_rate_hz)
        nyquist = sample_rate_hz / 2
        if config.low_pass_cutoff_hz >= nyquist:
            raise ValueError(
                f"Set the low-pass cutoff below {nyquist:g} Hz or turn it off."
            )
        if config.suppress_50hz:
            if 50 >= nyquist:
                raise ValueError("Turn off 50 Hz suppression for this sample rate.")
            stages.append(tf2sos(*iirnotch(50, Q=30, fs=sample_rate_hz)))
        if config.low_pass_cutoff_hz:
            stages.append(
                butter(4, config.low_pass_cutoff_hz, fs=sample_rate_hz, output="sos")
            )

    filtered = raw.copy()
    if not stages and not config.remove_dc_offset:
        return filtered

    coefficients = np.vstack(stages) if stages else None
    for column in channels:
        samples = raw[column].to_numpy(dtype=float, copy=True)
        finite = np.isfinite(samples)
        if coefficients is not None:
            # Filter each uninterrupted run so missing samples don't contaminate a channel.
            edges = np.flatnonzero(np.diff(finite, prepend=False, append=False))
            for start, end in edges.reshape(-1, 2):
                samples[start:end] = sosfiltfilt(
                    coefficients, samples[start:end], padtype=None
                )
        if config.remove_dc_offset and finite.any():
            samples[finite] -= samples[finite].mean()
        filtered[column] = samples
    return filtered


def recording_sample_rate(raw: pd.DataFrame, recorded_rate: float | None) -> float:
    """Use the recorded clock rate or infer it from uniform CSV timestamps."""
    if recorded_rate is not None:
        return validate_sample_rate(recorded_rate)
    if "t_(s)" in raw and len(raw) >= 2:
        intervals = np.diff(raw["t_(s)"].to_numpy(dtype=float))
        interval = float(np.median(intervals))
        # CSV export rounds timestamps, so allow small differences between samples.
        if (
            interval > 0
            and np.isfinite(interval)
            and np.allclose(intervals, interval, rtol=1e-3, atol=0)
        ):
            return 1 / interval
    raise ValueError(
        "Load recording metadata or use data with evenly spaced timestamps."
    )


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
