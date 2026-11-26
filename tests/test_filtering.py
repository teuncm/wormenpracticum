import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.filter.filter_controller import FilterController
from app.feature.filter.filter_view import FilterView


def test_filter_tab_reprocesses_raw_recording_and_can_restore_it():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = FilterView()
    controller = FilterController(model, view)
    controls = view.filter_controls
    try:
        assert not controls.apply_button.isEnabled()
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
        assert controls.apply_button.isEnabled()
        original = raw.copy()
        controls.cutoff.setValue(100)
        controls.apply_button.click()
        first_result = model.filtered_data_df.copy()
        pd.testing.assert_frame_equal(model.raw_data_df, original)
        np.testing.assert_array_equal(first_result["t_(s)"], times)
        assert abs(first_result["pin1"].mean()) < 1e-10
        for frequency in (50, 200):
            tone = np.sin(2 * np.pi * frequency * times)
            assert abs(first_result["pin1"].to_numpy() @ tone) < 0.2 * (
                raw["pin1"].to_numpy() @ tone
            )

        controls.apply_button.click()
        pd.testing.assert_frame_equal(model.filtered_data_df, first_result)
        controls.cutoff.setValue(600)
        controls.apply_button.click()
        assert "below 500 Hz" in controls.status.text()
        pd.testing.assert_frame_equal(model.filtered_data_df, first_result)

        controls.cutoff.setValue(0)
        controls.suppress_50hz.setChecked(False)
        controls.remove_dc.setChecked(False)
        controls.apply_button.click()
        pd.testing.assert_frame_equal(model.filtered_data_df, original)
        model.clear_experiment_data()
        assert not controls.apply_button.isEnabled()
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_cutoff_drag_updates_filtered_preview_before_release():
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
        controls.cutoff_slider.setSliderDown(True)

        # Wait for the published result while the slider is still held down.
        update = QEventLoop()
        model.experiment_data_changed.connect(update.quit)
        controls.cutoff_slider.setSliderPosition(160)
        QTimer.singleShot(3000, update.quit)
        update.exec()
        model.experiment_data_changed.disconnect(update.quit)

        assert controls.cutoff_slider.isSliderDown()
        assert model.filtered_data_df is not raw
        assert model.filtered_data_df["pin1"].std() < raw["pin1"].std() / 5
        x, y = view.preview_curve.getOriginalDataset()
        np.testing.assert_array_equal(x, times)
        np.testing.assert_array_equal(y, model.filtered_data_df["pin1"])

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
