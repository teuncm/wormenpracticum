"""Identify stimulus responses inside a continuous recording."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator


@dataclass
class StimulusResponse:
    """One recorded response and the peak magnitude of its sampled AO waveform."""

    number: int
    times_s: np.ndarray
    samples_v: np.ndarray
    stimulus_voltage_v: float | None

    def extrema(self) -> dict[str, tuple[float, float]]:
        """Return the first finite minimum and maximum on the recording timeline."""
        finite_indices = np.flatnonzero(np.isfinite(self.samples_v))
        if not finite_indices.size:
            return {}
        samples = self.samples_v[finite_indices]
        # NumPy argmin/argmax select the first occurrence when values are tied.
        indices = {
            "min": finite_indices[np.argmin(samples)],
            "max": finite_indices[np.argmax(samples)],
        }
        return {
            kind: (float(self.times_s[index]), float(self.samples_v[index]))
            for kind, index in indices.items()
        }


def split_stimulus_responses(
    data: pd.DataFrame, column: str, metadata: dict, config: dict
) -> list[StimulusResponse]:
    """Use recorded sample boundaries and settings, never the live designer state."""
    size = metadata.get("stimulus_size_samples")
    count = metadata.get("stimulus_count")
    rate = metadata.get("sample_rate_hz")
    if type(size) is not int or size <= 0 or type(count) is not int or count <= 0:
        raise ValueError("Stimulus size and count are missing or invalid.")
    if not isinstance(rate, (int, float)) or not np.isfinite(rate) or rate <= 0:
        raise ValueError("Recorded sample rate is missing or invalid.")
    if len(data) != size * count or metadata.get("sample_count", len(data)) != len(
        data
    ):
        raise ValueError("Recorded samples do not match the stimulus boundaries.")

    voltages = [None] * count
    if "stim_config" in config:
        saved = dict(config["stim_config"])
        saved["pulses"] = [Pulse(**pulse) for pulse in saved["pulses"]]
        generator = StimulusGenerator(StimulusConfig(**saved))
        if (
            len(generator.stims) != count
            or generator.config.stim.n_samples(rate) != size
        ):
            raise ValueError("Recorded stimulus settings do not match the recording.")
        voltages = [
            float(np.max(np.abs(generator.sample_at_idx(rate, step)[0])))
            for step in range(count)
        ]

    timestamps = data["t_(s)"].to_numpy()
    samples = data[column].to_numpy()
    return [
        StimulusResponse(
            step + 1,
            timestamps[step * size : (step + 1) * size],
            samples[step * size : (step + 1) * size],
            voltages[step],
        )
        for step in range(count)
    ]
