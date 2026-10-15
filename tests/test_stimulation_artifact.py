"""Check artifact timing without changing the propagated response."""

import numpy as np
import pytest

from app.feature.analysis.io_recording import split_stimulus_responses
from app.shared import data_io
from tools.propagation_data_gen import gen_propagation_recording
from tools.stimulation_artifact import gen_artifact_recording, write_artifact_recording


@pytest.mark.parametrize("divider", [1, 2])
def test_positive_artifact_precedes_each_wave_by_constant_delay(divider):
    options = {"stimulus_count": 3, "sample_rate_divider": divider}
    original, _ = gen_propagation_recording(**options)
    data, payload = gen_artifact_recording(**options)
    metadata = payload["metadata"]
    artifact = metadata["stimulation_artifact"]
    propagation = metadata["propagation"]
    size = metadata["stimulus_size_samples"]
    rate = metadata["sample_rate_hz"]
    assert 0 <= 0.001 - artifact["lead_s"] < 1 / rate
    np.testing.assert_array_equal(data["t_(s)"], original["t_(s)"])

    for wire, column in enumerate(metadata["pin_channels"]):
        wave_start = (
            propagation["start_sample"] + wire * propagation["wire_delay_samples"]
        )
        for stimulus in range(3):
            offset = stimulus * size
            samples = data[column].to_numpy()[offset : offset + size]
            assert np.argmax(samples) == wave_start - artifact["lead_samples"]
            assert samples.max() == pytest.approx(0.05)
            np.testing.assert_array_equal(
                samples[wave_start:],
                original[column].to_numpy()[offset + wave_start : offset + size],
            )
            assert samples.min() == pytest.approx(-0.005)


def test_artifact_csv_and_metadata_load_into_analysis(tmp_path):
    csv_path, json_path = write_artifact_recording(
        tmp_path / "artifact.csv", stimulus_count=2
    )
    data = data_io.read_data(csv_path)
    metadata, config = data_io.read_recording_metadata(json_path)
    responses = split_stimulus_responses(data, "ai0_(V)", metadata, config)
    assert len(responses) == 2
    assert metadata["stimulation_artifact"]["amplitude_v"] == 0.05
    assert responses[0].samples_v.max() == pytest.approx(0.05)


@pytest.mark.parametrize(
    "options",
    [
        {"artifact_amplitude_v": float("nan")},
        {"artifact_lead_s": 0},
        {"artifact_lead_s": 0.00001},
        {"artifact_lead_s": 0.01},
        {"artifact_width_s": -1},
        {"artifact_width_s": 0.01},
    ],
)
def test_invalid_artifact_timing_is_rejected(options):
    with pytest.raises(ValueError):
        gen_artifact_recording(**options)
