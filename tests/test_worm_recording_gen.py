"""Exercise synthetic recordings against the real CSV/JSON load and save paths."""

import os
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from app.app_controller import AppController
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator
from app.shared import data_dialog, data_io
from tools.worm_recording_gen import gen_dummy_recording, write_dummy_recording


@pytest.mark.parametrize("stimulus_count", [1, 3, 10])
@pytest.mark.parametrize("divider", [1, 4, 1024])
def test_generated_recording_layout_and_stimulus_boundaries(stimulus_count, divider):
    data, payload = gen_dummy_recording(0.5137, stimulus_count, divider)
    metadata = payload["metadata"]
    size = metadata["stimulus_size_samples"]
    rate = 15600 / divider
    assert size == int(0.5137 * rate)
    assert data.shape == (size * stimulus_count, 17)
    assert list(data.columns) == ["t_(s)", *[f"ai{i}_(V)" for i in range(16)]]
    assert metadata["sample_count"] == len(data)
    assert metadata["pin_channels"] == {f"ai{i}_(V)": i + 1 for i in range(16)}
    np.testing.assert_array_equal(data["t_(s)"], np.arange(len(data)) / rate)
    assert np.isfinite(data.to_numpy()).all()

    # Every pin's next stimulus occupies the next rows, with stepped amplitude.
    for pin in range(16):
        first = data[f"ai{pin}_(V)"].to_numpy()[:size]
        assert np.any(first != 0)
        for step in range(stimulus_count):
            actual = data[f"ai{pin}_(V)"].to_numpy()[step * size : (step + 1) * size]
            np.testing.assert_allclose(actual, first * (step + 1), atol=1e-14)

    # The stored stimulus settings reconstruct exactly the same sample timeline.
    config = dict(payload["stim_config"])
    config["pulses"] = [Pulse(**pulse) for pulse in config["pulses"]]
    generator = StimulusGenerator(StimulusConfig(**config))
    waveform, times = generator.sample_all(rate)
    assert len(waveform) == len(data)
    np.testing.assert_array_equal(times, data["t_(s)"])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration_s": 0},
        {"duration_s": -1},
        {"duration_s": float("nan")},
        {"duration_s": float("inf")},
        {"duration_s": 1e-10},
        {"stimulus_count": 0},
        {"stimulus_count": -1},
        {"stimulus_count": 1.5},
        {"sample_rate_divider": 3},
        {"sample_rate_divider": 0},
    ],
)
def test_invalid_recording_parameters(kwargs):
    with pytest.raises(ValueError):
        gen_dummy_recording(**kwargs)


def test_generated_recording_load_and_resave(monkeypatch, tmp_path):
    app = QApplication.instance() or QApplication([])
    csv_path, json_path = write_dummy_recording(
        tmp_path / "input" / "synthetic.csv", 0.01, 3, 4
    )
    expected_data = data_io.read_data(csv_path)
    expected_payload = data_io.read_metadata(json_path)
    assert set(expected_payload) == {"metadata", "experiment_config", "stim_config"}
    assert expected_payload["metadata"]["file"] == "synthetic"
    for key in ("save_user", "save_date", "save_time"):
        assert expected_payload["metadata"][key]

    monkeypatch.setattr(data_dialog, "show_load_dialog", lambda: str(csv_path))
    monkeypatch.setattr(
        QMessageBox, "exec", lambda dialog: QMessageBox.StandardButton.Ok
    )
    controller = AppController()
    try:
        controller.load_experiment_data()
        pd.testing.assert_frame_equal(controller.app_model.raw_data_df, expected_data)
        assert controller.app_model.experiment_metadata == expected_payload["metadata"]
        assert (
            controller.app_model.experiment_config
            == expected_payload["experiment_config"]
        )
        controller.app_model.update_stim_config(StimulusConfig(0.2, 3.0, [], n_steps=7))
        output_path = tmp_path / "resaved.csv"
        monkeypatch.setattr(data_dialog, "show_save_dialog", lambda: str(output_path))
        controller.save_experiment_data()
        pd.testing.assert_frame_equal(data_io.read_data(output_path), expected_data)
        saved = data_io.read_metadata(output_path.with_suffix(".json"))
        assert saved["stim_config"] == expected_payload["stim_config"]
        assert saved["experiment_config"] == expected_payload["experiment_config"]
        for key, value in expected_payload["metadata"].items():
            if key not in ("file", "save_user", "save_date", "save_time"):
                assert saved["metadata"][key] == value
        assert saved["metadata"]["file"] == "resaved"
    finally:
        controller.app_view.close()
        app.processEvents()


def test_csv_precision_round_trip(tmp_path):
    expected, _ = gen_dummy_recording(0.05, 4, 1)
    csv_path, json_path = write_dummy_recording(tmp_path / "precision.csv", 0.05, 4, 1)
    actual = data_io.read_data(csv_path)
    np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=1e-10)
    assert data_io.read_metadata(json_path)["metadata"]["sample_count"] == len(actual)


def test_generator_cli(tmp_path):
    output_path = tmp_path / "cli.csv"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.worm_recording_gen",
            "--output",
            str(output_path),
            "--duration",
            "0.02",
            "--stimuli",
            "2",
            "--divider",
            "4",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Wrote" in result.stdout
    data = data_io.read_data(output_path)
    assert data.shape == (156, 17)
    assert (
        data_io.read_metadata(output_path.with_suffix(".json"))["metadata"][
            "stimulus_count"
        ]
        == 2
    )
