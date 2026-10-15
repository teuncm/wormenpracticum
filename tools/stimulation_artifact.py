"""Generate propagated peak/trough waves with a preceding stimulation artifact.

Run from the project root: uv run python -m tools.stimulation_artifact
The CSV and JSON sidecar can be loaded directly into the analysis windows.
"""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from app.feature.acquisition.protocol_config import SAMPLE_RATE_DIVIDERS
from app.feature.stimulus.signal import quantize_time_point
from app.shared import data_io
from tools.propagation_data_gen import gen_propagation_recording


def gen_artifact_recording(
    artifact_amplitude_v: float = 0.05,
    artifact_lead_s: float = 0.001,
    artifact_width_s: float = 0.0002,
    **propagation_options,
) -> tuple[pd.DataFrame, dict]:
    """Add a narrow positive Gaussian spike before every wire's wave onset.

    The artifact is ten times the response amplitude by default. Its lead time
    is constant across wires and stimuli, quantized to the recording clock.
    The original propagated peak and trough remain intact.
    """
    for name, value in (
        ("artifact_amplitude_v", artifact_amplitude_v),
        ("artifact_lead_s", artifact_lead_s),
        ("artifact_width_s", artifact_width_s),
    ):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")

    data, payload = gen_propagation_recording(**propagation_options)
    metadata = payload["metadata"]
    rate = metadata["sample_rate_hz"]
    propagation = metadata["propagation"]
    lead = quantize_time_point(artifact_lead_s, rate)
    # Include a central sample even when the requested spike is narrower than a sample.
    radius = max(1, math.ceil(artifact_width_s * rate / 2))
    first_center = propagation["start_sample"] - lead
    if lead <= radius:
        raise ValueError(
            "The artifact must finish before the wave begins; increase its lead or reduce its width"
        )
    if first_center < radius:
        raise ValueError(
            "The first artifact starts before the recording; increase start_s or reduce artifact_lead_s"
        )

    offsets = np.arange(-radius, radius + 1)
    spike = artifact_amplitude_v * np.exp(-0.5 * (offsets / (radius / 3)) ** 2)
    size = metadata["stimulus_size_samples"]
    for wire, column in enumerate(metadata["pin_channels"]):
        center = first_center + wire * propagation["wire_delay_samples"]
        samples = data[column].to_numpy(copy=True)
        for stimulus in range(metadata["stimulus_count"]):
            offset = stimulus * size + center
            samples[offset - radius : offset + radius + 1] += spike
        data[column] = samples

    metadata["device_name"] = "SyntheticStimulationArtifactDAQ"
    metadata["stimulation_artifact"] = {
        "shape": "gaussian",
        "amplitude_v": artifact_amplitude_v,
        "lead_samples": lead,
        "lead_s": lead / rate,
        "width_samples": 2 * radius + 1,
        "first_center_sample": first_center,
    }
    return data, payload


def write_artifact_recording(
    output_path: Path | str = "data/stimulation_artifact.csv", **options
) -> tuple[Path, Path]:
    """Save the synthetic recording and metadata with the app's existing writers."""
    csv_path = Path(output_path)
    if csv_path.suffix.lower() != ".csv":
        raise ValueError("output_path must end in .csv")
    data, payload = gen_artifact_recording(**options)
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
    """Write example data with configurable artifact timing and magnitude."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("data/stimulation_artifact.csv")
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
        help="Wave peak/trough magnitude in mV",
    )
    parser.add_argument(
        "--start-ms", type=float, default=3.0, help="Wave onset at wire 1 in ms"
    )
    parser.add_argument(
        "--delay-ms", type=float, default=0.2, help="Propagation delay per wire in ms"
    )
    parser.add_argument(
        "--artifact-mv", type=float, default=50.0, help="Positive artifact peak in mV"
    )
    parser.add_argument(
        "--artifact-lead-ms",
        type=float,
        default=1.0,
        help="Time from artifact peak to wave onset in ms",
    )
    parser.add_argument(
        "--artifact-width-ms",
        type=float,
        default=0.2,
        help="Approximate spike width in ms",
    )
    args = parser.parse_args()
    try:
        paths = write_artifact_recording(
            args.output,
            duration_s=args.duration,
            stimulus_count=args.stimuli,
            sample_rate_divider=args.divider,
            amplitude_v=args.amplitude_mv / 1000,
            start_s=args.start_ms / 1000,
            wire_delay_s=args.delay_ms / 1000,
            artifact_amplitude_v=args.artifact_mv / 1000,
            artifact_lead_s=args.artifact_lead_ms / 1000,
            artifact_width_s=args.artifact_width_ms / 1000,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Wrote {paths[0]} and {paths[1]}")


if __name__ == "__main__":
    main()
