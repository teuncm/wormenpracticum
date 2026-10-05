import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QPushButton

from app.app_model import AppModel
from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.acquisition.protocol_controller import ProtocolController
from app.feature.acquisition.protocol_view import PinStateButton, ProtocolView
from app.feature.filter.filter_controller import FilterController


def test_sample_rate_dropdown_updates_rate_and_protocol():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = ProtocolView()
    controller = ProtocolController(model, view)

    try:
        view.set_max_sample_rate(20000)
        combo = view.ui.sampleRateDividerComboBox
        expected_dividers = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        assert [combo.itemData(i) for i in range(combo.count())] == expected_dividers
        combo.setCurrentIndex(combo.findData(4))
        assert model.protocol_config.sample_rate_divider == 4
        assert view.ui.maxSampleRateLabel.text() == "20000 Hz"
        assert view.ui.actualSampleRateLabel.text() == "5000 Hz"

        model.update_protocol_config(ProtocolConfig(0, 1, [3], 200))
        assert combo.currentData() == 256
        assert view.ui.actualSampleRateLabel.text() == "78.125 Hz"
        assert [combo.itemData(i) for i in range(combo.count())] == expected_dividers
        controller.update_ui_from_model()
        assert view.to_config() == model.protocol_config
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_record_and_apply_records_before_applying_settings():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = ProtocolView()
    controller = FilterController(model, view)
    events = []
    view.run_requested.connect(lambda: events.append("record"))
    model.filter_config_changed.connect(lambda: events.append("apply"))

    try:
        view.ui.lowPassHzDoubleSpinBox.setValue(250.0)
        view.ui.recordAndApplyButton.click()
        assert events == ["record", "apply"]
        assert model.filter_config.low_pass_cutoff_hz == 250.0
        controller.update_ui_from_model()
        layout = view.ui.leftLayout
        assert layout.indexOf(view.ui.pushButton) < layout.indexOf(view.ui.formLayout_2)
        assert layout.indexOf(view.ui.formLayout_2) < layout.indexOf(
            view.ui.filterActionsLayout
        )
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_filter_settings_apply_only_when_requested():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = ProtocolView()
    controller = FilterController(model, view)

    try:
        original_config = model.filter_config
        view.ui.lowPassHzDoubleSpinBox.setValue(250.0)
        view.ui.suppress50HzCheckBox.setChecked(False)
        view.ui.removeDCOffsetCheckBox.setChecked(False)
        assert model.filter_config == original_config

        view.ui.pushButton_2.click()
        assert model.filter_config == view.to_filter_config()
        assert model.filter_config.low_pass_cutoff_hz == 250.0

        view.ui.lowPassHzDoubleSpinBox.setValue(300.0)
        assert model.filter_config.low_pass_cutoff_hz == 250.0
        view.ui.lowPassHzDoubleSpinBox.setValue(400.0)
        view.ui.suppress50HzCheckBox.setChecked(True)
        view.ui.removeDCOffsetCheckBox.setChecked(True)
        assert model.filter_config.low_pass_cutoff_hz == 250.0
        assert not model.filter_config.suppress_50hz
        assert not model.filter_config.remove_dc_offset
        view.ui.pushButton_2.click()
        assert model.filter_config == view.to_filter_config()

        view.ui.lowPassHzDoubleSpinBox.setValue(500.0)
        assert model.filter_config.low_pass_cutoff_hz == 400.0
        controller.update_ui_from_model()
        assert view.ui.lowPassHzDoubleSpinBox.value() == 400.0
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()


def test_pin_colors_and_selection_keep_plot_range_stable(monkeypatch):
    # The offscreen Qt platform does not provide an OpenGL context.
    monkeypatch.setitem(pg.CONFIG_OPTIONS, "useOpenGL", False)
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = ProtocolView()
    controller = ProtocolController(model, view)

    try:
        view.show()
        app.processEvents()
        original_range = np.array(view.plotWidget.viewRange())
        bars = view.plotWidget.listDataItems()
        assert len(bars) == 16
        assert view.get_selected_stim_channels() == (1, 2)
        assert view.to_config().selected_pins == list(range(3, 17))
        expected_colors = ["#c92a2a", "#1971c2"] + ["#2f9e44"] * 14
        for button, bar, color in zip(view.pinButtons, bars, expected_colors):
            assert button.pin_color() == color
            assert bar.opts["pen"].color() == pg.mkColor(color)

        for state, color in (
            (PinStateButton.GREEN_STATE, "#2f9e44"),
            (PinStateButton.RED_STATE, "#c92a2a"),
            (PinStateButton.BLUE_STATE, "#1971c2"),
            (PinStateButton.DEFAULT_STATE, "gray"),
        ):
            view.pinButtons[0].set_pin_state(state)
            app.processEvents()
            assert bars[0].opts["pen"].color() == pg.mkColor(color)
            assert view.plotWidget.listDataItems() == bars
            np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)

        view.pinButtons[1].set_pin_state(PinStateButton.DEFAULT_STATE)
        for name, color in (
            ("selectAllPinsButton", "#2f9e44"),
            ("deselectAllPinsButton", "gray"),
        ):
            view.findChild(QPushButton, name).click()
            app.processEvents()
            assert all(bar.opts["pen"].color() == pg.mkColor(color) for bar in bars)
            np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)

        # Select All preserves input/output colors and fills unused pins in green.
        view.pinButtons[0].set_pin_state(PinStateButton.RED_STATE)
        view.pinButtons[1].set_pin_state(PinStateButton.BLUE_STATE)
        view.pinButtons[2].set_pin_state(PinStateButton.GREEN_STATE)
        view.findChild(QPushButton, "selectAllPinsButton").click()
        app.processEvents()
        expected_colors = ["#c92a2a", "#1971c2"] + ["#2f9e44"] * 14
        for button, bar, color in zip(view.pinButtons, bars, expected_colors):
            assert button.pin_color() == color
            assert bar.opts["pen"].color() == pg.mkColor(color)
        assert model.protocol_config.selected_pins == list(range(3, 17))
        np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)

        # Deselect All clears green pins while keeping input/output assignments.
        view.findChild(QPushButton, "deselectAllPinsButton").click()
        app.processEvents()
        expected_colors = ["#c92a2a", "#1971c2"] + ["gray"] * 14
        for button, bar, color in zip(view.pinButtons, bars, expected_colors):
            assert button.pin_color() == color
            assert bar.opts["pen"].color() == pg.mkColor(color)
        assert model.protocol_config.selected_pins == []
        np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)

        # Model-driven refreshes must update colors as well as the buttons.
        view.pinButtons[0].set_pin_state(PinStateButton.BLUE_STATE)
        controller.update_ui_from_model()
        app.processEvents()
        assert bars[0].opts["pen"].color() == pg.mkColor("#c92a2a")
        np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
