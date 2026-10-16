"""Check logarithmic zoom consistently across all analysis windows."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from app.feature.analysis.analyze_view_io import AnalyzeIOView
from app.feature.analysis.analyze_view_speed import AnalyzeSpeedView
from app.feature.analysis.analyze_view_tetanus import AnalyzeTetanusView
from app.feature.analysis.analyze_view_yolo import AnalyzeYoloView
from tools.worm_recording_gen import gen_dummy_recording


@pytest.mark.parametrize(
    "window_type",
    [AnalyzeIOView, AnalyzeSpeedView, AnalyzeTetanusView, AnalyzeYoloView],
)
def test_zoom_is_logarithmic_and_preserves_pin_positions_and_recording(window_type):
    app = QApplication.instance() or QApplication([])
    view = window_type()
    try:
        assert not view.vertical_zoom.isEnabled()
        data, payload = gen_dummy_recording(0.02, 2, 4)
        original = data.copy(deep=True)
        view.set_data(data, payload["metadata"], payload["experiment_config"])
        view.ui.amplitudeSpinBox.setValue(16.0)
        view.plot_widget.setXRange(0.002, 0.008, padding=0)
        time_range = view.plot_widget.viewRange()[0]
        count = 1 if isinstance(view, AnalyzeIOView) else 16
        assert view.vertical_zoom.isEnabled()

        for position in (0, 50, 100, 150, 200, 0):
            view.vertical_zoom.slider.setValue(position)
            factor = 100 ** (position / 200)
            assert view.vertical_zoom.factor == pytest.approx(factor)
            lower, upper = view.plot_widget.viewRange()[1]
            span = 16.0 / factor
            assert upper - lower == pytest.approx(span)
            assert view.ui.amplitudeSpinBox.value() == 16.0
            assert view.plot_widget.viewRange()[0] == pytest.approx(time_range)
            if isinstance(view, AnalyzeIOView):
                assert (lower, upper) == pytest.approx((-span / 2, span / 2))
                np.testing.assert_array_equal(
                    view.curve.getOriginalDataset()[1], data["ai0_(V)"]
                )
            else:
                for rank, label in enumerate(view.pin_labels):
                    assert (label.pos().y() - lower) / span == pytest.approx(
                        (rank + 0.5) / count
                    )
                # Zoom never scales measured voltage stored in marker tooltips.
                assert all(
                    np.isfinite(point.data()["voltage_v"])
                    for point in view.peak_markers.points()
                )

        view.vertical_zoom.slider.setValue(200)
        view.set_data(data.copy(), payload["metadata"], payload["experiment_config"])
        assert view.vertical_zoom.factor == 100.0
        assert np.ptp(view.plot_widget.viewRange()[1]) == pytest.approx(0.16)
        view.ui.amplitudeSpinBox.setValue(8.0)
        assert np.ptp(view.plot_widget.viewRange()[1]) == pytest.approx(0.08)
        pd.testing.assert_frame_equal(data, original)

        view.set_data(None)
        assert not view.vertical_zoom.isEnabled()
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
