import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtCore import QPointF
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


def test_preview_keeps_sequence_scale_and_clamps_step_when_sequence_shrinks():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = StimulusView()
    controller = StimulusController(model, view)

    def configure_steps(count):
        controller.app_model.update_stim_config(
            StimulusConfig(
                dur_s=0.01,
                limit_v=1.5,
                n_steps=count,
                pulses=[Pulse(amp_v=0.2, start_s=0.001, dur_s=0.002, step_amp_v=0.3)],
            )
        )

    try:
        configure_steps(3)
        start_range = view.plotWidget.viewRange()[1]
        assert start_range[1] >= 0.8
        assert view.ui.stimulusPositionLabel.text() == "Stimulus 1 of 3"

        view.ui.stepSlider.setValue(2)
        assert view.ui.stimulusPositionLabel.text() == "Stimulus 3 of 3"
        assert view.plotWidget.viewRange()[1] == pytest.approx(start_range)

        configure_steps(1)
        assert view.ui.stepSlider.value() == view.ui.stepSlider.maximum() == 0
        assert view.ui.stimulusPositionLabel.text() == "Stimulus 1 of 1"
        assert view.plotWidget.viewRange()[1][1] < start_range[1]
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_pulse_handles_edit_base_fields_from_a_stepped_preview():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = StimulusView()
    controller = StimulusController(model, view)
    try:
        controller.app_model.update_stim_config(
            StimulusConfig(
                dur_s=0.02,
                limit_v=1.5,
                n_steps=3,
                pulses=[
                    Pulse(
                        amp_v=-0.4,
                        start_s=0.003,
                        dur_s=0.003,
                        step_amp_v=-0.1,
                        step_start_s=0.001,
                        step_dur_s=0.001,
                    )
                ],
            )
        )
        view.ui.stepSlider.setValue(2)
        assert view.start_handle.isVisible() and view.end_handle.isVisible()
        assert view.start_handle.pos().y() == pytest.approx(0.6)
        assert view.end_handle.pos().y() == pytest.approx(0.0)
        # A manual zoom must survive both the drag update and its release.
        view.plotWidget.setYRange(-0.9, 0.9, padding=0)
        original_range = view.plotWidget.viewRange()
        tab = view.ui.segmentTabWidget.currentWidget()

        view.start_handle.moving = True
        view.start_handle.dragged.emit(QPointF(0.007, 0.8))
        assert view.ui.segmentTabWidget.currentWidget() is tab
        assert view.plotWidget.viewRange() == original_range
        view.start_handle.moving = False
        view.start_handle.sigPositionChangeFinished.emit(view.start_handle)
        assert view.plotWidget.viewRange() == original_range

        view.end_handle.dragged.emit(QPointF(0.015, 0.4))
        pulse = model.stim_config.stim.pulses[0]
        assert (pulse.start_s, pulse.amp_v, pulse.dur_s) == pytest.approx(
            (0.005, -0.6, 0.006)
        )
        assert (pulse.step_start_s, pulse.step_amp_v, pulse.step_dur_s) == (
            0.001,
            -0.1,
            0.001,
        )
        assert (
            view.ui.segmentTabWidget.currentWidget().spinboxes["dur_s"].value() == 0.006
        )

        # A later step can collapse even when the base duration is positive.
        view.ui.segmentTabWidget.currentWidget().spinboxes["step_dur_s"].setValue(
            -0.003
        )
        assert not view.start_handle.isVisible()
        assert view.end_handle.isVisible()
        assert view.end_handle.pos() == QPointF(0.007, 0.0)
        view.end_handle.dragged.emit(QPointF(0.009, 0.0))
        assert model.stim_config.stim.pulses[0].dur_s == pytest.approx(0.008)
        assert view.start_handle.isVisible()

        view.ui.highlight_selected_pulse_checkbox.setChecked(False)
        assert not view.start_handle.isVisible()
        assert not view.end_handle.isVisible()
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
