from pathlib import Path

import pandas as pd
import pytest

from app.shared.data_io import (
    read_data,
    read_recording_metadata,
    write_data,
    write_metadata,
)


def test_save_load_data(tmp_path):
    """Verify that loaded data equals saved data using the data I/O functions."""
    test_df = pd.DataFrame(
        {"Timestamp (s)": [0.0, 0.001, 0.002], "Channel 1 (V)": [0.1, 0.2, 0.3]}
    )

    file_path = Path(tmp_path) / "test_data.csv"

    write_data(file_path, test_df)
    loaded_df = read_data(file_path)

    pd.testing.assert_frame_equal(test_df, loaded_df)


@pytest.mark.parametrize(
    ("metadata", "error"),
    [
        ({"sample_rate_hz": True}, "sample rate"),
        ({"sample_rate_hz": float("inf")}, "sample rate"),
        ({"sample_count": 4.0}, "sample count"),
        ({"sample_count": 5}, "sample count"),
        ({"stimulus_size_samples": 3, "stimulus_count": 2}, "stimulus boundaries"),
        ({"pin_channels": []}, "pin channels"),
        ({"pin_channels": {"ai0_(V)": 0}}, "pin channels"),
    ],
)
def test_load_rejects_invalid_recording_metadata(tmp_path, metadata, error):
    sidecar = tmp_path / "recording.json"
    write_metadata(sidecar, {"metadata": metadata})

    result = read_recording_metadata(sidecar, row_count=4)

    assert isinstance(result, str)
    assert error in result.lower()


def test_load_accepts_legacy_sidecar_with_partial_metadata(tmp_path):
    sidecar = tmp_path / "recording.json"
    metadata = {"pin_channels": {"ai0_(V)": "1"}, "run": 3}
    stimulus = {"pulses": []}
    write_metadata(sidecar, {"metadata": metadata, "stim_config": stimulus})

    assert read_recording_metadata(sidecar, row_count=4) == (
        metadata,
        {"stim_config": stimulus},
    )
