"""Generate delayed sinusoidal peaks and troughs in the app's recording format.

Run from the project root: uv run python -m tools.propagation_data_gen
Wire 1 is ai0_(V); each subsequent wire receives the same response slightly later.
"""

import argparse
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from app.feature.acquisition.protocol_config import SAMPLE_RATE_DIVIDERS, ProtocolConfig
from app.feature.nidaq.nidaq_constants import NI_DAQ_BASE_SAMPLE_RATE_HZ
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.signal import get_time_frame_s, quantize_time_point
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.shared import data_io
from app.shared.constants import DEFAULT_LIMIT_V


def gen_propagation_recording(
    duration_s: float = 0.02,
    stimulus_count: int = 10,
    sample_rate_divider: int = 1,
    amplitude_v: float = 0.005,
    peak_width_s: float = 0.002,
    start_s: float = 0.003,
    wire_delay_s: float = 0.0002,
) -> tuple[pd.DataFrame, dict]:
    """Return one sine cycle per wire, with a positive peak then a negative trough.

    Repeat the propagation pattern for every stimulus. Timing is quantized to
    sample indices so the waveform stays identical as it moves across wires.
    The JSON sidecar supplies the boundaries required by the analysis pages.
    """
    for name, value in (
        ("duration_s", duration_s),
        ("amplitude_v", amplitude_v),
        ("peak_width_s", peak_width_s),
        ("wire_delay_s", wire_delay_s),
    ):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    if not math.isfinite(start_s) or start_s < 0:
        raise ValueError("start_s must be finite and nonnegative")
    if type(stimulus_count) is not int or stimulus_count <= 0:
        raise ValueError("stimulus_count must be a positive integer")
    if sample_rate_divider not in SAMPLE_RATE_DIVIDERS:
        raise ValueError("sample_rate_divider must be a supported power of two")

    rate = NI_DAQ_BASE_SAMPLE_RATE_HZ / sample_rate_divider
    size = quantize_time_point(duration_s, rate)
    start = quantize_time_point(start_s, rate)
    width = quantize_time_point(peak_width_s, rate)
    delay = quantize_time_point(wire_delay_s, rate)
    if width < 4:
        raise ValueError("peak_width_s must span at least four sample intervals")
    if delay < 1:
        raise ValueError("wire_delay_s must span at least one sample interval")
    if start + 15 * delay + width >= size:
        raise ValueError(
            "duration_s must contain the complete response on all 16 wires"
        )

    # One full sine cycle gives a peak and trough, with zero baseline on both sides.
    response = np.sin(np.linspace(0, 2 * np.pi, width + 1))
    response[[0, -1]] = 0.0
    response *= amplitude_v / np.max(np.abs(response))
    pin_channels = {f"ai{wire}_(V)": wire + 1 for wire in range(16)}
    data = {"t_(s)": get_time_frame_s(size * stimulus_count, rate)}
    for wire, column in enumerate(pin_channels):
        samples = np.zeros(size)
        offset = start + wire * delay
        samples[offset : offset + len(response)] = response
        data[column] = np.tile(samples, stimulus_count)

    # The excitation precedes the simulated response and repeats without stepping.
    stim_config = StimulusConfig(
        dur_s=duration_s,
        limit_v=DEFAULT_LIMIT_V,
        pulses=[Pulse(amp_v=0.1, start_s=0.0, dur_s=0.0002, is_monophasic=True)],
        n_steps=stimulus_count,
    ).to_dict()
    protocol = ProtocolConfig(0, 1, list(range(3, 17)), sample_rate_divider)
    payload = {
        "metadata": {
            "device_name": "SyntheticPropagationDAQ",
            "sample_rate_hz": rate,
            "stimulus_size_samples": size,
            "stimulus_count": stimulus_count,
            "sample_count": size * stimulus_count,
            "pin_channels": pin_channels,
            "propagation": {
                "shape": "full_sine",
                "amplitude_v": amplitude_v,
                "start_sample": start,
                "peak_width_samples": width,
                "wire_delay_samples": delay,
            },
        },
        "experiment_config": {
            "stim_config": stim_config,
            "protocol_config": asdict(protocol),
        },
        "stim_config": stim_config,
    }
    return pd.DataFrame(data), payload


def write_propagation_recording(
    output_path: Path | str = "data/propagation_recording.csv", **kwargs
) -> tuple[Path, Path]:
    """Write the synthetic CSV and matching JSON sidecar for File → Load data."""
    csv_path = Path(output_path)
    if csv_path.suffix.lower() != ".csv":
        raise ValueError("output_path must end in .csv")
    data, payload = gen_propagation_recording(**kwargs)
    json_path = csv_path.with_suffix(".json")
    payload["metadata"]["file"] = csv_path.stem
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    for path, content, writer in (
        (csv_path, data, data_io.write_data),
        (json_path, payload, data_io.write_metadata),
    ):
        error = writer(path, content)
        if error:
            raise OSError(f"Error saving {path}: {error}")
    return csv_path, json_path


def main() -> None:
    """Generate example data with configurable response size and propagation delay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("data/propagation_recording.csv")
    )
    parser.add_argument(
        "--duration", type=float, default=0.02, help="Seconds per stimulus"
    )
    parser.add_argument("--stimuli", type=int, default=10)
    parser.add_argument("--divider", type=int, choices=SAMPLE_RATE_DIVIDERS, default=1)
    parser.add_argument(
        "--amplitude-mv",
        type=float,
        default=5.0,
        help="Peak and trough magnitude in mV",
    )
    parser.add_argument(
        "--peak-width-ms", type=float, default=2.0, help="Full sine-cycle width in ms"
    )
    parser.add_argument(
        "--start-ms", type=float, default=3.0, help="Response onset at wire 1 in ms"
    )
    parser.add_argument(
        "--delay-ms", type=float, default=0.2, help="Delay per wire in ms"
    )
    args = parser.parse_args()
    try:
        csv_path, json_path = write_propagation_recording(
            args.output,
            duration_s=args.duration,
            stimulus_count=args.stimuli,
            sample_rate_divider=args.divider,
            amplitude_v=args.amplitude_mv / 1000,
            peak_width_s=args.peak_width_ms / 1000,
            start_s=args.start_ms / 1000,
            wire_delay_s=args.delay_ms / 1000,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Wrote {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
