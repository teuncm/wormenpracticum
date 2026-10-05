import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.analysis.analyze_speed_controller import AnalyzeSpeedController
from app.feature.analysis.analyze_view_speed import AnalyzeSpeedView
from tools.worm_recording_gen import gen_dummy_recording


@pytest.fixture
def speed_analysis():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = AnalyzeSpeedView()
    controller = AnalyzeSpeedController(model, view)
    yield model, view, controller
    view.close()
    view.deleteLater()
    app.processEvents()


def test_speed_shows_one_stimulus_across_all_pins_with_offsets(speed_analysis):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    original = data.copy()
    size = payload["metadata"]["stimulus_size_samples"]
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert view.ui.stimulusComboBox.count() == 3
    assert len(view.curves) == len(view.pin_labels) == 16
    view.ui.stimulusComboBox.setCurrentIndex(1)
    view.ui.offsetSpinBox.setValue(0.2)
    for pin, curve in enumerate(view.curves):
        x, y = curve.getOriginalDataset()
        segment = data.iloc[size : 2 * size]
        np.testing.assert_allclose(x, segment["t_(s)"] - segment["t_(s)"].iloc[0])
        np.testing.assert_array_equal(y, segment[f"ai{pin}_(V)"] + pin * 0.2)
        assert view.pin_labels[pin].toPlainText() == f"Pin {pin + 1}"
    assert "Voltage axis refers to Pin 1" in view.ui.recordingStatusLabel.text()
    assert np.array_equal(data.to_numpy(), original.to_numpy())

    filtered = data.copy()
    filtered["ai3_(V)"] *= 2
    model.update_filtered_data(filtered)
    assert view.ui.stimulusComboBox.currentIndex() == 1
    assert view.ui.offsetSpinBox.value() == 0.2
    np.testing.assert_allclose(
        view.curves[3].getOriginalDataset()[1],
        filtered["ai3_(V)"].iloc[size : 2 * size] + 0.6,
    )


def test_speed_uses_physical_pin_order_and_saved_sample_boundaries(speed_analysis):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.0137, 2, 4)
    data = data[["t_(s)", "ai15_(V)", "ai2_(V)", "ai0_(V)"]]
    data["t_(s)"] += 5
    model.update_recording(data, payload["metadata"], {})
    assert [label.toPlainText() for label in view.pin_labels] == [
        "Pin 1",
        "Pin 3",
        "Pin 16",
    ]
    view.ui.stimulusComboBox.setCurrentIndex(1)
    size = payload["metadata"]["stimulus_size_samples"]
    x, y = view.curves[0].getOriginalDataset()
    assert len(x) == size
    assert x[0] == 0
    np.testing.assert_array_equal(y, data["ai0_(V)"].iloc[size:])


@pytest.mark.parametrize(
    "metadata_change",
    [{"stimulus_size_samples": 0}, {"stimulus_count": 100}, {"sample_rate_hz": 0}],
)
def test_speed_clears_traces_for_invalid_recordings(speed_analysis, metadata_change):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    payload["metadata"].update(metadata_change)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert not view.curves
    assert not view.pin_labels
    assert not view.ui.stimulusComboBox.isEnabled()
    assert "Cannot select stimuli" in view.ui.recordingStatusLabel.text()


def test_speed_resets_selection_for_shorter_recording_and_clears(speed_analysis):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.stimulusComboBox.setCurrentIndex(2)
    data, payload = gen_dummy_recording(0.02, 1, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert view.ui.stimulusComboBox.currentIndex() == 0
    assert len(view.curves) == 16
    model.clear_experiment_data()
    assert not view.curves
    assert not view.pin_labels
    assert not view.ui.stimulusComboBox.isEnabled()


@pytest.mark.parametrize(
    "show_min, show_max", [(True, False), (False, True), (True, True), (False, False)]
)
def test_speed_extrema_checkboxes_keep_offsets_and_report_raw_voltage(
    speed_analysis, show_min, show_max
):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.02, 2, 4)
    size = payload["metadata"]["stimulus_size_samples"]
    for pin in range(16):
        data[f"ai{pin}_(V)"] = np.concatenate(
            [
                np.resize([-0.8, -0.8, 0.4, 0.4], size),
                np.resize([0.2, 0.2, -0.6, -0.6], size),
            ]
        ) * (pin + 1)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.offsetSpinBox.setValue(2.0)
    assert view.ui.minCheckBox.isChecked() and view.ui.maxCheckBox.isChecked()
    curves = list(view.curves)
    view.plot_widget.setRange(xRange=(0.001, 0.005), yRange=(-1, 1), padding=0)
    previous_range = view.plot_widget.viewRange()
    view.ui.minCheckBox.setChecked(show_min)
    view.ui.maxCheckBox.setChecked(show_max)
    assert view.curves == curves
    assert view.plot_widget.viewRange() == previous_range
    for stimulus in range(2):
        view.ui.stimulusComboBox.setCurrentIndex(stimulus)
        points = view.peak_markers.points()
        assert len(points) == 16 * (show_min + show_max)
        for point in points:
            info = point.data()
            pin = int(info["pin"].split()[1])
            minimum = info["kind"] == "minimum"
            sample = (0 if minimum else 2) if stimulus == 0 else (2 if minimum else 0)
            voltage = (
                (-0.8 if minimum else 0.4)
                if stimulus == 0
                else (-0.6 if minimum else 0.2)
            )
            voltage *= pin
            expected_time = (
                data["t_(s)"].iloc[stimulus * size + sample]
                - data["t_(s)"].iloc[stimulus * size]
            )
            assert point.pos().x() == expected_time
            assert point.pos().y() == voltage + (pin - 1) * 2
            assert info["voltage_v"] == voltage
            tooltip = view._peak_tooltip(point.pos().x(), point.pos().y(), info)
            assert f"Pin {pin} · Stimulus {stimulus + 1}" in tooltip
            assert f"Recorded {info['kind']}: {voltage:.6g} V" in tooltip


def test_speed_extrema_skip_nonfinite_pins_and_clear_with_recording(speed_analysis):
    model, view, _ = speed_analysis
    data, payload = gen_dummy_recording(0.02, 1, 4)
    data["ai0_(V)"] = np.nan
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert len(view.peak_markers.points()) == 30
    assert all(point.data()["pin"] != "Pin 1" for point in view.peak_markers.points())
    model.clear_experiment_data()
    assert len(view.peak_markers.points()) == 0
    assert not view.ui.minCheckBox.isEnabled()
    assert not view.ui.maxCheckBox.isEnabled()
