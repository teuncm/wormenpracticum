"""Verify propagation timing and compatibility with stimulus analysis."""

import numpy as np
import pytest

from app.feature.analysis.io_recording import split_stimulus_responses
from app.shared import data_io
from tools.propagation_data_gen import (
    gen_propagation_recording,
    write_propagation_recording,
)


@pytest.mark.parametrize("divider", [1, 2])
def test_peak_and_trough_propagate_without_changing_shape(divider):
    data, payload = gen_propagation_recording(
        stimulus_count=3, sample_rate_divider=divider
    )
    metadata = payload["metadata"]
    size = metadata["stimulus_size_samples"]
    delay = metadata["propagation"]["wire_delay_samples"]
    first_wire = data["ai0_(V)"].to_numpy()[:size]
    first_peak = np.argmax(first_wire)
    first_trough = np.argmin(first_wire)
    assert data.shape == (3 * size, 17)
    assert first_wire.max() == pytest.approx(0.005)
    assert first_wire.min() == pytest.approx(-0.005)
    assert first_peak < first_trough
    np.testing.assert_array_equal(
        data["t_(s)"], np.arange(len(data)) / metadata["sample_rate_hz"]
    )

    for wire in range(16):
        column = f"ai{wire}_(V)"
        responses = split_stimulus_responses(
            data, column, metadata, payload["experiment_config"]
        )
        assert metadata["pin_channels"][column] == wire + 1
        assert len(responses) == 3
        expected = np.roll(first_wire, wire * delay)
        for response in responses:
            np.testing.assert_array_equal(response.samples_v, expected)
            assert np.argmax(response.samples_v) == first_peak + wire * delay
            assert np.argmin(response.samples_v) == first_trough + wire * delay
            assert response.samples_v[0] == response.samples_v[-1] == 0.0
            assert response.samples_v.min() == pytest.approx(-0.005)


def test_written_recording_can_be_loaded_and_split(tmp_path):
    csv_path, json_path = write_propagation_recording(tmp_path / "propagation.csv")
    data = data_io.read_data(csv_path)
    metadata, config = data_io.read_recording_metadata(json_path)
    responses = split_stimulus_responses(data, "ai15_(V)", metadata, config)
    assert len(responses) == 10
    assert responses[0].samples_v.max() == pytest.approx(0.005)
    assert responses[0].samples_v.min() == pytest.approx(-0.005)
    assert responses[0].stimulus_voltage_v == pytest.approx(0.1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration_s": 0.001},
        {"amplitude_v": float("nan")},
        {"stimulus_count": 0},
        {"start_s": -1},
        {"peak_width_s": 0.000001},
        {"peak_width_s": 0.0002},
        {"wire_delay_s": 0.000001},
        {"sample_rate_divider": 3},
    ],
)
def test_invalid_or_unresolvable_propagation_is_rejected(kwargs):
    with pytest.raises(ValueError):
        gen_propagation_recording(**kwargs)
