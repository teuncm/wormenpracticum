import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.filter.filter_controller import FilterController
from app.feature.filter.filter_controls import FilterControls
from app.feature.filter.filter_view import FilterView


def test_filter_tab_reprocesses_raw_recording_and_can_restore_it():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = FilterView()
    controller = FilterController(model, view)
    controls = view.filter_controls
    try:
        assert not controls.low_pass.isEnabled()
        assert not controls.suppress_50hz.isChecked()
        assert not controls.remove_dc.isChecked()
        times = np.arange(2000) / 1000
        raw = pd.DataFrame(
            {
                "t_(s)": times,
                "pin1": 2
                + np.sin(2 * np.pi * 10 * times)
                + np.sin(2 * np.pi * 50 * times)
                + np.sin(2 * np.pi * 200 * times),
            }
        )
        controller.app_model.update_recording(raw, {"sample_rate_hz": 1000}, {})
        assert controls.low_pass.isEnabled()
        original = raw.copy()
        controls.cutoff.setValue(100)
        controls.suppress_50hz.setChecked(True)
        controls.remove_dc.setChecked(True)
        controller.apply_filters(controls)
        first_result = model.filtered_data_df.copy()
        pd.testing.assert_frame_equal(model.raw_data_df, original)
        np.testing.assert_array_equal(first_result["t_(s)"], times)
        assert abs(first_result["pin1"].mean()) < 1e-10
        for frequency in (50, 200):
            tone = np.sin(2 * np.pi * frequency * times)
            assert abs(first_result["pin1"].to_numpy() @ tone) < 0.2 * (
                raw["pin1"].to_numpy() @ tone
            )

        controller.apply_filters(controls)
        pd.testing.assert_frame_equal(model.filtered_data_df, first_result)
        controls.cutoff.setValue(600)
        controller.apply_filters(controls)
        assert "below 500 Hz" in controls.status.text()
        pd.testing.assert_frame_equal(model.filtered_data_df, first_result)

        controls.low_pass.setChecked(False)
        controls.suppress_50hz.setChecked(False)
        controls.remove_dc.setChecked(False)
        controller.apply_filters(controls)
        pd.testing.assert_frame_equal(model.filtered_data_df, original)
        assert model.filter_config.low_pass_cutoff_hz == 0
        assert controls.cutoff.value() == 100
        assert not controls.cutoff_slider.isEnabled()

        controls.low_pass.setChecked(True)
        controller.apply_filters(controls)
        assert model.filter_config.low_pass_cutoff_hz == 100
        assert controls.cutoff_slider.isEnabled()
        assert not model.filtered_data_df.equals(original)

        model.clear_experiment_data()
        assert not controls.low_pass.isEnabled()
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_cutoff_slider_maps_linear_steps_to_frequency():
    app = QApplication.instance() or QApplication([])
    controls = FilterControls()
    controls.set_sample_rate(1000)
    slider = controls.cutoff_slider

    try:
        for position, cutoff in ((100, 166.34), (200, 332.67), (300, 499), (0, 0.01)):
            slider.setValue(position)
            assert controls.cutoff.value() == cutoff

        controls.cutoff.setValue(332.67)
        assert slider.value() == 200
    finally:
        controls.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("auto_update", [True, False])
def test_cutoff_drag_updates_filtered_preview_at_the_selected_time(auto_update):
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = FilterView()
    controller = FilterController(model, view)
    controls = view.filter_controls
    try:
        times = np.arange(1000) / 1000
        raw = pd.DataFrame(
            {"t_(s)": times, "pin1": np.sin(2 * np.pi * 150 * times), "pin2": times}
        )
        original = raw.copy()
        controller.app_model.update_recording(raw, {}, {})
        controls.suppress_50hz.setChecked(False)
        controls.remove_dc.setChecked(False)
        controls.auto_update.setChecked(auto_update)
        controls.cutoff_slider.setSliderDown(True)

        update = QEventLoop()
        model.experiment_data_changed.connect(update.quit)
        controls.cutoff_slider.setSliderPosition(30)
        if not auto_update:
            # Wait beyond the live-update interval to check that the drag hasn't applied.
            QTest.qWait(80)
            assert model.filtered_data_df is raw
            controls.cutoff_slider.setSliderDown(False)

        QTimer.singleShot(3000, update.quit)
        update.exec()
        model.experiment_data_changed.disconnect(update.quit)

        assert controls.cutoff_slider.isSliderDown() == auto_update
        assert controls.status.isHidden()
        assert model.filtered_data_df is not raw
        assert model.filtered_data_df["pin1"].std() < raw["pin1"].std() / 5
        x, y = view.preview_curve.getOriginalDataset()
        np.testing.assert_array_equal(x, times)
        np.testing.assert_array_equal(y, model.filtered_data_df["pin1"])

        controls.cutoff_slider.setValue(0)
        controller.apply_filters(controls)
        assert controls.low_pass.isChecked()
        assert controls.cutoff_slider.isEnabled()
        assert model.filter_config.low_pass_cutoff_hz == controls.cutoff.minimum()

        filtered = model.filtered_data_df
        view.channel_selector.setCurrentIndex(1)
        assert model.filtered_data_df is filtered
        np.testing.assert_array_equal(
            view.preview_curve.getOriginalDataset()[1], filtered["pin2"]
        )
        pd.testing.assert_frame_equal(model.raw_data_df, original)
        model.clear_experiment_data()
        assert view.preview_curve.getOriginalDataset() == (None, None)
        assert not controls.cutoff_slider.isEnabled()
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
