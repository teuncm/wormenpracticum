import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication, QComboBox

from app.app_model import AppModel
from app.feature.analysis.analyze_tetanus_controller import AnalyzeTetanusController
from app.feature.analysis.analyze_view_tetanus import AnalyzeTetanusView
from tools.worm_recording_gen import gen_dummy_recording


@pytest.fixture
def tetanus_analysis():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = AnalyzeTetanusView()
    controller = AnalyzeTetanusController(model, view)
    yield model, view, controller
    view.close()
    view.deleteLater()
    app.processEvents()


def test_tetanus_shows_all_samples_and_pins_without_selectors(tetanus_analysis):
    model, view, _ = tetanus_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.offsetSpinBox.setValue(0.2)
    assert not view.findChildren(QComboBox)
    assert len(view.curves) == len(view.pin_labels) == 16
    for pin, curve in enumerate(view.curves):
        x, y = curve.getOriginalDataset()
        np.testing.assert_array_equal(x, data["t_(s)"])
        np.testing.assert_array_equal(y, data[f"ai{pin}_(V)"] + pin * 0.2)
        assert view.pin_labels[pin].toPlainText() == f"Pin {pin + 1}"
    filtered = data.copy()
    filtered["ai3_(V)"] *= 2
    model.update_filtered_data(filtered)
    np.testing.assert_allclose(
        view.curves[3].getOriginalDataset()[1], filtered["ai3_(V)"] + 0.6
    )
    assert view.ui.offsetSpinBox.value() == 0.2


@pytest.mark.parametrize(
    "show_min, show_max", [(True, False), (False, True), (True, True), (False, False)]
)
def test_tetanus_extrema_per_stimulus_and_pin(tetanus_analysis, show_min, show_max):
    model, view, _ = tetanus_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    size = payload["metadata"]["stimulus_size_samples"]
    for pin in range(16):
        data[f"ai{pin}_(V)"] = np.tile(np.resize([-0.8, -0.8, 0.4, 0.4], size), 3) * (
            pin + 1
        )
    data["t_(s)"] += 5
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.offsetSpinBox.setValue(2.0)
    curves = list(view.curves)
    view.plot_widget.setRange(xRange=(5.001, 5.005), yRange=(-1, 1), padding=0)
    previous_range = view.plot_widget.viewRange()
    view.ui.minCheckBox.setChecked(show_min)
    view.ui.maxCheckBox.setChecked(show_max)
    assert view.curves == curves
    assert view.plot_widget.viewRange() == previous_range
    points = view.peak_markers.points()
    assert len(points) == 16 * 3 * (show_min + show_max)
    for point in points:
        info = point.data()
        pin = int(info["pin"].split()[1])
        minimum = info["kind"] == "minimum"
        sample = (info["number"] - 1) * size + (0 if minimum else 2)
        voltage = (-0.8 if minimum else 0.4) * pin
        assert point.pos().x() == data["t_(s)"].iloc[sample]
        assert point.pos().y() == voltage + (pin - 1) * 2
        assert info["voltage_v"] == voltage
        tooltip = view._peak_tooltip(point.pos().x(), point.pos().y(), info)
        assert f"Pin {pin} · Stimulus {info['number']}" in tooltip
        assert f"Recorded {info['kind']}: {voltage:.6g} V" in tooltip


def test_tetanus_replaces_measurements_and_clears(tetanus_analysis):
    model, view, _ = tetanus_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    old_curves = list(view.curves)
    data, payload = gen_dummy_recording(0.01, 1, 4)
    data = data[["t_(s)", "ai15_(V)", "ai0_(V)"]]
    data["ai15_(V)"] = np.nan
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    assert [label.toPlainText() for label in view.pin_labels] == ["Pin 1", "Pin 16"]
    assert len(view.peak_markers.points()) == 2
    assert all(point.data()["number"] == 1 for point in view.peak_markers.points())
    assert all(curve not in view.plot_widget.listDataItems() for curve in old_curves)
    np.testing.assert_array_equal(
        view.curves[0].getOriginalDataset()[1], data["ai0_(V)"]
    )
    model.clear_experiment_data()
    assert not view.curves
    assert not view.pin_labels
    assert len(view.peak_markers.points()) == 0
    assert not view.ui.minCheckBox.isEnabled()
    assert not view.ui.maxCheckBox.isEnabled()


@pytest.mark.parametrize("metadata", [{}, {"stimulus_size_samples": 0}])
def test_tetanus_keeps_full_traces_when_boundaries_are_missing(
    tetanus_analysis, metadata
):
    model, view, _ = tetanus_analysis
    data, _ = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, metadata, {})
    assert len(view.curves) == 16
    assert len(view.peak_markers.points()) == 0
    assert not view.ui.minCheckBox.isEnabled()
    assert "Min/max detection unavailable" in view.ui.recordingStatusLabel.text()
