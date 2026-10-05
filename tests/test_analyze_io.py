import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.analysis.analyze_io_controller import AnalyzeIOController
from app.feature.analysis.analyze_view_io import AnalyzeIOView
from app.feature.analysis.io_recording import StimulusResponse, split_stimulus_responses
from tools.worm_recording_gen import gen_dummy_recording


@pytest.fixture
def io_analysis():
    """Create the IO model, view, and controller without requiring a display."""
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = AnalyzeIOView()
    controller = AnalyzeIOController(model, view)
    yield model, view, controller
    view.close()
    view.deleteLater()
    app.processEvents()


def test_io_uses_filtered_sequence_and_switches_channels(io_analysis):
    """Display all ten received stimuli and select channels from filtered data."""
    model, view, _ = io_analysis
    times = np.arange(100) / 10
    raw = pd.DataFrame({"t_(s)": times, "ai0_(V)": times, "ai1_(V)": -times})
    model.update_raw_data(raw)
    filtered = raw.copy()
    filtered["ai0_(V)"] = np.repeat(np.arange(10), 10)
    filtered["ai1_(V)"] = filtered["ai0_(V)"] * -0.5
    model.update_filtered_data(filtered)

    x, y = view.curve.getData()
    np.testing.assert_array_equal(x, times)
    np.testing.assert_array_equal(y, filtered["ai0_(V)"])
    assert view.ui.channelSlider.maximum() == 2
    assert view.ui.channelSlider.isEnabled()

    view.ui.channelSlider.setValue(2)
    np.testing.assert_array_equal(view.curve.getData()[1], filtered["ai1_(V)"])
    assert view.ui.channelLabel.text() == "Channel 02: ai1_(V)"

    # Refreshing a filter must preserve the selected channel and update its trace.
    filtered = filtered.copy()
    filtered["ai1_(V)"] *= 2
    model.update_filtered_data(filtered)
    assert view.ui.channelSlider.value() == 2
    np.testing.assert_array_equal(view.curve.getData()[1], filtered["ai1_(V)"])


def test_io_handles_missing_data_and_replacement_channels(io_analysis):
    """Clear stale traces and safely adjust the slider when recordings change."""
    model, view, _ = io_analysis
    assert not view.ui.channelSlider.isEnabled()
    assert view.curve.getData()[0] is None

    model.update_filtered_data(
        pd.DataFrame(
            {
                "t_(s)": [0.0, 0.1],
                "ai0_(V)": [1.0, 2.0],
                "ai1_(V)": [3.0, 4.0],
            }
        )
    )
    view.ui.channelSlider.setValue(2)
    model.update_filtered_data(
        pd.DataFrame(
            {
                "t_(s)": [0.0, 0.1],
                "ai0_(V)": [5.0, 6.0],
            }
        )
    )
    assert view.ui.channelSlider.value() == 1
    assert not view.ui.channelSlider.isEnabled()
    np.testing.assert_array_equal(view.curve.getData()[1], [5.0, 6.0])

    for data in (pd.DataFrame(), pd.DataFrame({"ai0_(V)": [1.0]})):
        model.update_filtered_data(data)
        assert view.curve.getData()[0] is None
        assert view.ui.channelLabel.text() == "Channel: no data"


def test_io_plots_one_concatenated_trace_and_marks_peaks_for_selected_pin(io_analysis):
    model, view, _ = io_analysis
    data, payload = gen_dummy_recording(0.01, 3, 4)
    metadata = payload["metadata"]
    size = metadata["stimulus_size_samples"]
    model.update_recording(data, metadata, payload["experiment_config"])
    view.ui.minCheckBox.setChecked(False)
    assert view.pin_selector.count() == 16
    assert view.plot_widget.listDataItems() == [view.curve, view.peak_markers]
    original_curve = view.curve
    np.testing.assert_array_equal(view.curve.getData()[0], data["t_(s)"])
    np.testing.assert_array_equal(view.curve.getData()[1], data["ai0_(V)"])
    assert len(view.peak_markers.points()) == 3
    assert "Synthetic signals" in view.recording_status.text()

    view.pin_selector.setCurrentIndex(8)
    assert view.ui.channelLabel.text() == "Pin 9: ai8_(V)"
    assert view.plot_widget.listDataItems() == [original_curve, view.peak_markers]
    np.testing.assert_array_equal(view.curve.getData()[0], data["t_(s)"])
    np.testing.assert_array_equal(view.curve.getData()[1], data["ai8_(V)"])
    for step in range(3):
        expected = data["ai8_(V)"].to_numpy()[step * size : (step + 1) * size]
        peak = view.peak_markers.points()[step]
        index = np.argmax(expected)
        assert peak.pos().y() == expected[index]
        assert peak.pos().x() == data["t_(s)"].iloc[step * size + index]
        tooltip = view._peak_tooltip(peak.pos().x(), peak.pos().y(), peak.data())
        assert f"Pin 9 · Stimulus {step + 1}" in tooltip
        assert f"Recorded maximum: {expected[index]:.6g} V" in tooltip
        assert "Stimulation output peak:" in tooltip

    filtered = data.copy()
    filtered["ai8_(V)"] *= -2
    model.update_filtered_data(filtered)
    assert view.pin_selector.currentIndex() == 8
    assert view.plot_widget.listDataItems() == [original_curve, view.peak_markers]
    assert len(view.peak_markers.points()) == 3
    np.testing.assert_array_equal(view.curve.getData()[1], filtered["ai8_(V)"])

    model.clear_experiment_data()
    assert view.curve.getData() == (None, None)
    assert len(view.peak_markers.points()) == 0
    assert not view.pin_selector.isEnabled()


@pytest.mark.parametrize(
    "samples, expected_min, expected_max",
    [
        ([0.1, -0.7, 0.5], (0.1, -0.7), (0.2, 0.5)),
        ([float("nan"), 0.4, float("inf")], (0.1, 0.4), (0.1, 0.4)),
        ([float("nan"), float("nan"), float("nan")], None, None),
        ([0.0, 0.0, 0.0], (0.0, 0.0), (0.0, 0.0)),
        ([-0.5, -0.5, -0.1], (0.0, -0.5), (0.2, -0.1)),
        ([0.1, 0.5, 0.5], (0.0, 0.1), (0.1, 0.5)),
    ],
)
def test_extrema_select_first_finite_minimum_and_maximum(
    samples, expected_min, expected_max
):
    response = StimulusResponse(1, np.arange(3) / 10, np.array(samples), 0.3)
    expected = (
        {} if expected_min is None else {"min": expected_min, "max": expected_max}
    )
    assert response.extrema() == expected


@pytest.mark.parametrize(
    "show_min, show_max", [(True, False), (False, True), (True, True), (False, False)]
)
def test_extrema_checkboxes_update_markers_only(io_analysis, show_min, show_max):
    model, view, _ = io_analysis
    data, payload = gen_dummy_recording(0.01, 3, 4)
    size = payload["metadata"]["stimulus_size_samples"]
    # Tied values make the expected first positions unambiguous for each stimulus.
    data["ai0_(V)"] = np.tile(np.resize([-0.8, -0.8, 0.4, 0.4], size), 3)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert view.ui.minCheckBox.isChecked() and view.ui.maxCheckBox.isChecked()
    view.plot_widget.setRange(xRange=(0.001, 0.005), yRange=(-1, 1), padding=0)
    previous_range = view.plot_widget.viewRange()
    view.ui.minCheckBox.setChecked(show_min)
    view.ui.maxCheckBox.setChecked(show_max)
    assert view.plot_widget.viewRange() == previous_range
    # getData() may clip to the visible range; the original dataset stays intact.
    x, y = view.curve.getOriginalDataset()
    np.testing.assert_array_equal(x, data["t_(s)"])
    np.testing.assert_array_equal(y, data["ai0_(V)"])
    points = view.peak_markers.points()
    assert len(points) == 3 * (show_min + show_max)
    for point in points:
        minimum = point.data()["kind"] == "minimum"
        offset = 0 if minimum else 2
        index = (point.data()["number"] - 1) * size + offset
        assert point.pos().x() == data["t_(s)"].iloc[index]
        assert point.pos().y() == (-0.8 if minimum else 0.4)
    view.pin_selector.setCurrentIndex(1)
    assert view.ui.minCheckBox.isChecked() == show_min
    assert view.ui.maxCheckBox.isChecked() == show_max
    assert len(view.peak_markers.points()) == len(points)


def test_stimulation_voltages_use_recorded_clipped_samples():
    data, payload = gen_dummy_recording(0.1, 3, 1)
    config = payload["experiment_config"]
    config["stim_config"]["limit_v"] = 0.25
    config["stim_config"]["pulses"][0]["amp_v"] = -0.2
    config["stim_config"]["pulses"][0]["step_amp_v"] = -0.1
    responses = split_stimulus_responses(data, "ai0_(V)", payload["metadata"], config)
    np.testing.assert_allclose(
        [response.stimulus_voltage_v for response in responses], [0.2, 0.25, 0.25]
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"stimulus_size_samples": 0},
        {"stimulus_size_samples": 1},
        {"stimulus_count": 2},
        {"sample_count": 1},
        {"sample_rate_hz": 0},
        {"sample_rate_hz": float("nan")},
    ],
)
def test_invalid_boundaries_do_not_invent_stimulus_traces(io_analysis, changes):
    model, view, _ = io_analysis
    data, payload = gen_dummy_recording(0.01, 3, 4)
    payload["metadata"].update(changes)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert view.plot_widget.listDataItems() == [view.curve, view.peak_markers]
    assert len(view.peak_markers.points()) == 0
    np.testing.assert_array_equal(view.curve.getData()[1], data["ai0_(V)"])
    assert "Peak markers unavailable:" in view.recording_status.text()


def test_missing_stimulus_config_still_displays_response_peaks(io_analysis):
    model, view, _ = io_analysis
    data, payload = gen_dummy_recording(0.01, 3, 4)
    model.update_recording(data, payload["metadata"], {})
    assert view.plot_widget.listDataItems() == [view.curve, view.peak_markers]
    assert len(view.peak_markers.points()) == 6
    point = view.peak_markers.points()[0]
    assert "Stimulation output peak: unavailable" in view._peak_tooltip(
        point.pos().x(), point.pos().y(), point.data()
    )
