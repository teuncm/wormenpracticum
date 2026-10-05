"""Generate synthetic CSV/JSON recordings in the current NI-DAQ save format.

Run from the project root: uv run python -m tools.worm_recording_gen
Stimuli follow each other down rows; the 16 physical pins have separate columns.
"""

import argparse
import getpass
import math
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from app.feature.acquisition.protocol_config import SAMPLE_RATE_DIVIDERS, ProtocolConfig
from app.feature.nidaq.nidaq_constants import NI_DAQ_BASE_SAMPLE_RATE_HZ
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator
from app.shared import data_io
from app.shared.constants import DEFAULT_LIMIT_V


def gen_dummy_recording(
    duration_s: float = 0.5,
    stimulus_count: int = 10,
    sample_rate_divider: int = 1,
) -> tuple[pd.DataFrame, dict]:
    """Return continuous pin data and a JSON payload ready for the save helpers.

    Each pin has a distinct sine frequency; amplitude increases with each
    stimulus. These deterministic signals test layout, not worm physiology.
    Stimulus duration is quantized exactly as in the stimulus generator.
    """
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("duration_s must be finite and positive")
    if type(stimulus_count) is not int or stimulus_count <= 0:
        raise ValueError("stimulus_count must be a positive integer")
    if sample_rate_divider not in SAMPLE_RATE_DIVIDERS:
        raise ValueError("sample_rate_divider must be a supported power of two")

    protocol = ProtocolConfig(0, 1, list(range(3, 17)), sample_rate_divider)
    rate = NI_DAQ_BASE_SAMPLE_RATE_HZ / sample_rate_divider
    stim_config = StimulusConfig(
        dur_s=duration_s,
        limit_v=DEFAULT_LIMIT_V,
        n_steps=stimulus_count,
        pulses=[
            Pulse(
                amp_v=0.1,
                start_s=duration_s / 10,
                dur_s=duration_s / 10,
                step_amp_v=0.1,
                is_monophasic=True,
            )
        ],
    )
    stimulus_size = stim_config.stim.n_samples(rate)
    if stimulus_size == 0:
        raise ValueError("duration_s must produce at least one sample per stimulus")
    generator = StimulusGenerator(stim_config)
    _, timestamps = generator.sample_all(rate)
    sample_indices = np.arange(len(timestamps))
    local_times = (sample_indices % stimulus_size) / rate
    step_amplitudes = (sample_indices // stimulus_size + 1) / stimulus_count
    pin_channels = {f"ai{i}_(V)": i + 1 for i in range(16)}
    data = {"t_(s)": timestamps}
    for index, column in enumerate(pin_channels):
        # Frequencies stay below Nyquist at every supported divider.
        frequency = rate * (index + 1) / 128
        data[column] = (
            0.05
            * (index + 1)
            * step_amplitudes
            * np.sin(2 * np.pi * frequency * local_times)
        )

    config = stim_config.to_dict()
    payload = {
        "metadata": {
            "device_name": "SyntheticDAQ",
            "sample_rate_hz": rate,
            "stimulus_size_samples": stimulus_size,
            "stimulus_count": stimulus_count,
            "sample_count": len(timestamps),
            "pin_channels": pin_channels,
        },
        "experiment_config": {
            "stim_config": config,
            "protocol_config": asdict(protocol),
        },
        "stim_config": config,
    }
    return pd.DataFrame(data), payload


def write_dummy_recording(
    output_path: Path | str = "data/test_recording.csv",
    duration_s: float = 0.5,
    stimulus_count: int = 10,
    sample_rate_divider: int = 1,
) -> tuple[Path, Path]:
    """Write a CSV and its same-named JSON sidecar using the app's writers."""
    csv_path = Path(output_path)
    if csv_path.suffix.lower() != ".csv":
        raise ValueError("output_path must end in .csv")
    data, payload = gen_dummy_recording(duration_s, stimulus_count, sample_rate_divider)
    json_path = csv_path.with_suffix(".json")
    now = datetime.now().astimezone()
    payload["metadata"].update(
        {
            "file": csv_path.stem,
            "save_user": getpass.getuser(),
            "save_date": now.date().isoformat(),
            "save_time": now.timetz().isoformat(),
        }
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    error = data_io.write_data(csv_path, data)
    if error:
        raise OSError(f"Error saving data: {error}")
    error = data_io.write_metadata(json_path, payload)
    if error:
        raise OSError(f"Error saving metadata: {error}")
    return csv_path, json_path


def main() -> None:
    """Generate a configurable recording for loading through the app UI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/test_recording.csv"))
    parser.add_argument(
        "--duration", type=float, default=0.5, help="Seconds per stimulus"
    )
    parser.add_argument("--stimuli", type=int, default=10)
    parser.add_argument("--divider", type=int, choices=SAMPLE_RATE_DIVIDERS, default=1)
    args = parser.parse_args()
    try:
        csv_path, json_path = write_dummy_recording(
            args.output, args.duration, args.stimuli, args.divider
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Wrote {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
