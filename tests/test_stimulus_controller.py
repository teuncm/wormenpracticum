import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.stimulus.stimulus_controller import StimulusController
from app.feature.stimulus.stimulus_view import StimulusView


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
