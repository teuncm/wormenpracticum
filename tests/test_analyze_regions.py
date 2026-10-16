import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit

from app.feature.analysis.analyze_view_io import AnalyzeIOView
from app.feature.analysis.analyze_view_speed import AnalyzeSpeedView
from app.feature.analysis.analyze_view_tetanus import AnalyzeTetanusView
from app.feature.analysis.io_recording import StimulusResponse
from app.feature.analysis.region_selection import (
    DetectionRegionEditor,
    bounded_extrema,
)
from tools.worm_recording_gen import gen_dummy_recording


@pytest.fixture
def qt_app():
    return QApplication.instance() or QApplication([])


def make_artifact_recording():
    """Create two traces whose large artifacts lie outside the nerve response."""
    data, payload = gen_dummy_recording(0.02, 2, 4)
    size = payload["metadata"]["stimulus_size_samples"]
    times = data["t_(s)"].to_numpy()
    for column in ("ai0_(V)", "ai1_(V)"):
        data[column] = 0.25
        for number in (1, 2):
            start = (number - 1) * size
            local_times = times[start : start + size] - times[start]
            in_region = np.flatnonzero((local_times >= 0.005) & (local_times <= 0.008))
            data.loc[data.index[start], column] = 100.0
            data.loc[data.index[start + in_region[0]], column] = -2.0
            data.loc[data.index[start + in_region[-1]], column] = 3.0
    return data[["t_(s)", "ai0_(V)", "ai1_(V)"]], payload


def apply_bounds(view, lower="5", upper="8"):
    view.ui.detectionStartLineEdit.setText(lower)
    view.ui.detectionEndLineEdit.setText(upper)
    view._apply_detection_region()


def test_shared_region_editor_retains_last_valid_bounds_and_extrema_are_finite(qt_app):
    lower, upper, error = QLineEdit(), QLineEdit(), QLabel()
    editor = DetectionRegionEditor(lower, upper, error)
    lower.setText("3")
    upper.setText("8")
    assert editor.apply()
    lower.setText("9")
    upper.setText("8")
    assert not editor.apply()
    assert editor.bounds_ms == (3.0, 8.0)
    assert error.text()

    response = StimulusResponse(
        1,
        np.array([0.0, 0.001, 0.002, 0.003]),
        np.array([100.0, np.nan, -2.0, 3.0]),
        None,
    )
    assert bounded_extrema(response, (2.0, 3.0)) == {
        "min": (0.002, -2.0),
        "max": (0.003, 3.0),
    }
    assert bounded_extrema(response, (4.0, 5.0)) == {}
    assert (
        bounded_extrema(
            StimulusResponse(1, response.times_s, np.full(4, np.nan), None),
            (None, None),
        )
        == {}
    )


@pytest.mark.parametrize(
    "window_type", [AnalyzeIOView, AnalyzeSpeedView, AnalyzeTetanusView]
)
def test_all_analysis_windows_bound_peaks_and_keep_region_on_refresh(
    qt_app, window_type
):
    data, payload = make_artifact_recording()
    metadata = {
        **payload["metadata"],
        "pin_channels": {"ai0_(V)": 1, "ai1_(V)": 2},
    }
    view = window_type()
    try:
        view.set_data(data, metadata, payload["experiment_config"])
        if isinstance(view, AnalyzeSpeedView):
            view.ui.stimulusComboBox.setCurrentIndex(1)
        if isinstance(view, AnalyzeIOView):
            view.pin_selector.setCurrentIndex(1)
        apply_bounds(view)

        points = view.peak_markers.points()
        expected_points = 8 if isinstance(view, AnalyzeTetanusView) else 4
        assert len(points) == expected_points
        assert {point.data().get("voltage_v", point.pos().y()) for point in points} == {
            -2.0,
            3.0,
        }
        assert all(
            point.data().get("voltage_v", point.pos().y()) != 100.0 for point in points
        )
        assert len(view.guide_lines["start"]) == (
            1 if isinstance(view, AnalyzeSpeedView) else 2
        )
        if isinstance(view, AnalyzeIOView):
            view.pin_selector.setCurrentIndex(0)
            assert view._detection_region_ms == (5.0, 8.0)
            view.pin_selector.setCurrentIndex(1)
        elif isinstance(view, AnalyzeSpeedView):
            view.ui.stimulusComboBox.setCurrentIndex(0)
            assert view._detection_region_ms == (5.0, 8.0)
            view.ui.stimulusComboBox.setCurrentIndex(1)

        before = np.array(view.plot_widget.viewRange())
        curves = [view.curve] if isinstance(view, AnalyzeIOView) else list(view.curves)
        apply_bounds(view, "100", "101")
        assert len(view.peak_markers.points()) == 0
        assert np.array_equal(view.plot_widget.viewRange(), before)
        assert curves == (
            [view.curve] if isinstance(view, AnalyzeIOView) else list(view.curves)
        )

        apply_bounds(view, "5", "8")
        filtered = data.copy()
        view.set_data(filtered, metadata, payload["experiment_config"])
        assert view._detection_region_ms == (5.0, 8.0)
        assert {
            point.data().get("voltage_v", point.pos().y())
            for point in view.peak_markers.points()
        } == {
            -2.0,
            3.0,
        }
    finally:
        view.close()
        view.deleteLater()
        qt_app.processEvents()


def test_region_clicks_map_full_and_local_plot_times(qt_app):
    data, payload = make_artifact_recording()
    size = payload["metadata"]["stimulus_size_samples"]
    metadata = {
        **payload["metadata"],
        "pin_channels": {"ai0_(V)": 1, "ai1_(V)": 2},
    }

    class Click:
        def __init__(self, view, button, x):
            self.view, self._button, self.x = view, button, x

        def button(self):

            return self._button

        def scenePos(self):
            from PySide6.QtCore import QPointF

            box = self.view.plot_widget.getPlotItem().getViewBox()
            return box.mapViewToScene(QPointF(self.x, 0.0))

    from PySide6.QtCore import Qt

    for view_type, timestamp in (
        (AnalyzeIOView, float(data["t_(s)"].iloc[size] + 0.006)),
        (AnalyzeTetanusView, float(data["t_(s)"].iloc[size] + 0.006)),
        (AnalyzeSpeedView, 0.006),
    ):
        view = view_type()
        try:
            view.set_data(data, metadata, payload["experiment_config"])
            if isinstance(view, AnalyzeSpeedView):
                view.ui.stimulusComboBox.setCurrentIndex(1)
            view.show()
            qt_app.processEvents()
            click = Click(view, Qt.MouseButton.LeftButton, timestamp)
            view._set_region_from_click(click)
            assert float(view.ui.detectionStartLineEdit.text()) == pytest.approx(6.0)
            assert view._detection_region_ms[0] == pytest.approx(6.0)
            assert view._local_stimulus_time(timestamp) == pytest.approx(0.006)
        finally:
            view.close()
            view.deleteLater()
            qt_app.processEvents()
