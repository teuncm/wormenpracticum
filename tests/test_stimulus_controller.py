import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_controller import StimulusController
from app.feature.stimulus.stimulus_view import StimulusView


@pytest.mark.parametrize("saved_limit", [0.5, 2.0])
def test_loaded_stimulus_uses_fixed_voltage_limit(saved_limit):
    model = AppModel()
    config = StimulusConfig(
        dur_s=0.01,
        limit_v=saved_limit,
        pulses=[Pulse(amp_v=2.0, start_s=0.0, dur_s=0.002)],
    )

    model.import_state({"stim_config": config.to_dict()})

    samples, _ = model.stim_generator.sample_at_idx(10000, 0)
    assert model.stim_config.limit_v == 1.5
    assert samples.min() == -1.5
    assert samples.max() == 1.5
    assert model.export_state()["stim_config"]["limit_v"] == 1.5


def test_added_pulses_follow_latest_end_with_two_millisecond_gap(monkeypatch):
    app = QApplication.instance() or QApplication([])
    errors = []
    monkeypatch.setattr(sys, "excepthook", lambda *error: errors.append(error))
    model = AppModel()
    model.update_stim_config(
        StimulusConfig(
            dur_s=0.1,
            limit_v=1.0,
            pulses=[
                Pulse(amp_v=0.5, start_s=0.01, dur_s=0.003),
                Pulse(amp_v=0.5, start_s=0.001, dur_s=0.002),
            ],
        )
    )
    view = StimulusView()
    controller = StimulusController(model, view)

    try:
        # Append in time even when the final tab is an earlier pulse.
        for expected_start in (0.015, 0.0172):
            view.ui.add_pulse_button.click()
            app.processEvents()
            assert model.stim_config.stim.pulses[-1].dur_s == pytest.approx(0.0002)
            assert model.stim_config.stim.pulses[-1].start_s == pytest.approx(
                expected_start
            )
            controller.update_ui_from_model()
            tabs = view.ui.segmentTabWidget
            assert tabs.widget(tabs.count() - 1).spinboxes[
                "start_s"
            ].value() == pytest.approx(expected_start)
        assert errors == []
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


@pytest.mark.parametrize("highlight", [False, True])
def test_delete_all_pulses_and_add_again(monkeypatch, highlight):
    app = QApplication.instance() or QApplication([])
    errors = []
    monkeypatch.setattr(sys, "excepthook", lambda *error: errors.append(error))
    model = AppModel()
    view = StimulusView()
    controller = StimulusController(model, view)

    try:
        view.ui.highlight_selected_pulse_checkbox.setChecked(highlight)
        view.ui.add_pulse_button.click()
        tabs = view.ui.segmentTabWidget
        while tabs.count():
            tabs.tabCloseRequested.emit(tabs.count() - 1)
        app.processEvents()

        assert model.stim_config.stim.pulses == []
        assert model.get_y_bounds() == (0.0, 0.0)
        controller.update_plot()
        curves = view.plotWidget.listDataItems()
        assert len(curves) == 1
        np.testing.assert_array_equal(curves[0].yData, 0.0)

        view.ui.highlight_selected_pulse_checkbox.setChecked(not highlight)
        view.ui.nSpinBox.setValue(3)
        view.ui.stepSlider.setValue(2)
        app.processEvents()
        controller.update_plot()

        view.ui.add_pulse_button.click()
        app.processEvents()
        assert tabs.count() == 1
        assert len(model.stim_config.stim.pulses) == 1
        controller.update_plot()
        assert errors == []
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
