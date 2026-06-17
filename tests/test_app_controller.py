import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from app.app_controller import AppController
from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.filter.filter_config import FilterConfig
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.shared import data_dialog, data_io
from app.shared.constants import (
    DEFAULT_FILTER_CONFIG,
    DEFAULT_PROTOCOL_CONFIG,
    DEFAULT_STIMULUS_CONFIG,
)


def test_load_data_action_is_connected(monkeypatch):
    app = QApplication.instance() or QApplication([])
    load_requests = []

    monkeypatch.setattr(
        AppController,
        "load_experiment_data",
        lambda self: load_requests.append(True),
    )

    controller = AppController()
    controller.app_view.ui.actionLoad_data.trigger()
    app.processEvents()

    assert load_requests == [True]
    controller.app_view.close()
    app.processEvents()


def test_load_protocol_action_is_connected(monkeypatch):
    app = QApplication.instance() or QApplication([])
    load_requests = []

    monkeypatch.setattr(
        AppController,
        "load_protocol_state",
        lambda self: load_requests.append(True),
    )

    controller = AppController()
    controller.app_view.ui.actionLoad_protocol.trigger()
    app.processEvents()

    assert load_requests == [True]
    controller.app_view.close()
    app.processEvents()


def test_state_filename_uses_typed_json_suffix():
    app = QApplication.instance() or QApplication([])
    controller = AppController()

    assert controller._state_filename("test.json", "stimulus").endswith(
        "test.stimulus.json"
    )
    assert controller._state_filename("test.protocol.json", "filter").endswith(
        "test.filter.json"
    )

    controller.app_view.close()
    app.processEvents()


def test_save_stimulus_state_writes_typed_json(monkeypatch):
    app = QApplication.instance() or QApplication([])
    writes = []

    monkeypatch.setattr(data_dialog, "show_save_json_dialog", lambda: "test.json")
    monkeypatch.setattr(
        data_io,
        "write_metadata",
        lambda filename, state: writes.append((filename, state)),
    )

    controller = AppController()
    controller.save_stimulus_state()

    assert writes[0][0].endswith("test.stimulus.json")
    assert set(writes[0][1]) == {"stim_config"}

    controller.app_view.close()
    app.processEvents()


def test_save_protocol_and_filter_actions_are_connected(monkeypatch):
    app = QApplication.instance() or QApplication([])
    save_requests = []

    monkeypatch.setattr(
        AppController,
        "save_protocol_state",
        lambda self: save_requests.append("protocol"),
    )
    monkeypatch.setattr(
        AppController,
        "save_filter_state",
        lambda self: save_requests.append("filter"),
    )

    controller = AppController()
    controller.app_view.ui.actionSave_protocol.trigger()
    controller.app_view.ui.actionSave_filter.trigger()
    app.processEvents()

    assert save_requests == ["protocol", "filter"]
    controller.app_view.close()
    app.processEvents()


def test_save_protocol_and_filter_state_write_typed_json(monkeypatch):
    app = QApplication.instance() or QApplication([])
    filenames = iter(["test.json", "test.json"])
    writes = []

    monkeypatch.setattr(data_dialog, "show_save_json_dialog", lambda: next(filenames))
    monkeypatch.setattr(
        data_io,
        "write_metadata",
        lambda filename, state: writes.append((filename, state)),
    )

    controller = AppController()
    controller.save_protocol_state()
    controller.save_filter_state()

    assert writes[0][0].endswith("test.protocol.json")
    assert set(writes[0][1]) == {"protocol_config"}
    assert writes[1][0].endswith("test.filter.json")
    assert set(writes[1][1]) == {"filter_config"}

    controller.app_view.close()
    app.processEvents()


def test_reset_config_actions_are_connected(monkeypatch):
    app = QApplication.instance() or QApplication([])
    reset_requests = []

    monkeypatch.setattr(
        AppController,
        "reset_stimulus_state",
        lambda self: reset_requests.append("stimulus"),
    )
    monkeypatch.setattr(
        AppController,
        "reset_protocol_state",
        lambda self: reset_requests.append("protocol"),
    )
    monkeypatch.setattr(
        AppController,
        "reset_filter_state",
        lambda self: reset_requests.append("filter"),
    )

    controller = AppController()
    controller.app_view.ui.actionReset_stimulus.trigger()
    controller.app_view.ui.actionReset_protocol.trigger()
    controller.app_view.ui.actionReset_filter.trigger()
    app.processEvents()

    assert reset_requests == ["stimulus", "protocol", "filter"]
    controller.app_view.close()
    app.processEvents()


def test_reset_config_actions_restore_default_configs():
    app = QApplication.instance() or QApplication([])
    controller = AppController()

    controller.app_model.update_stim_config(
        StimulusConfig(
            dur_s=0.1,
            limit_v=0.5,
            n_steps=1,
            pulses=[Pulse(amp_v=0.2, start_s=0.001, dur_s=0.001)],
        )
    )
    controller.app_model.update_protocol_config(
        ProtocolConfig(
            positive_channel=4,
            negative_channel=5,
            selected_pins=[6, 7],
            sample_rate_divider=2,
        )
    )
    controller.app_model.update_filter_config(
        FilterConfig(
            low_pass_cutoff_hz=250.0,
            suppress_50hz=False,
            remove_dc_offset=False,
        )
    )

    controller.app_view.ui.actionReset_stimulus.trigger()
    controller.app_view.ui.actionReset_protocol.trigger()
    controller.app_view.ui.actionReset_filter.trigger()
    app.processEvents()

    assert controller.app_model.stim_config == DEFAULT_STIMULUS_CONFIG
    assert controller.app_model.stim_config is not DEFAULT_STIMULUS_CONFIG
    assert controller.app_model.protocol_config == DEFAULT_PROTOCOL_CONFIG
    assert controller.app_model.protocol_config is not DEFAULT_PROTOCOL_CONFIG
    assert controller.app_model.filter_config == DEFAULT_FILTER_CONFIG
    assert controller.app_model.filter_config is not DEFAULT_FILTER_CONFIG
    assert (
        controller.protocol_view.ui.positiveChannelComboBox.currentIndex()
        == DEFAULT_PROTOCOL_CONFIG.positive_channel
    )
    assert (
        controller.protocol_view.ui.negativeChannelComboBox.currentIndex()
        == DEFAULT_PROTOCOL_CONFIG.negative_channel
    )
    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.isChecked()
    ] == DEFAULT_PROTOCOL_CONFIG.selected_pins
    assert (
        controller.protocol_view.ui.sampleRateDividerSpinBox.value()
        == DEFAULT_PROTOCOL_CONFIG.sample_rate_divider
    )
    assert (
        controller.overview_view.ui.doubleSpinBox.value()
        == DEFAULT_FILTER_CONFIG.low_pass_cutoff_hz
    )
    assert (
        controller.overview_view.ui.suppress50HzCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.suppress_50hz
    )
    assert (
        controller.overview_view.ui.removeDCOffsetCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.remove_dc_offset
    )

    controller.app_view.close()
    app.processEvents()


def test_reset_config_actions_restore_ui_after_ui_edits():
    app = QApplication.instance() or QApplication([])
    controller = AppController()

    controller.protocol_view.ui.positiveChannelComboBox.setCurrentIndex(3)
    controller.protocol_view.ui.negativeChannelComboBox.setCurrentIndex(4)
    controller.protocol_view.pinButtons[0].setChecked(True)
    controller.protocol_view.pinButtons[-1].setChecked(False)
    controller.protocol_view.ui.sampleRateDividerSpinBox.setValue(3)
    controller.overview_view.ui.doubleSpinBox.setValue(123.0)
    controller.overview_view.ui.suppress50HzCheckBox.setChecked(False)
    controller.overview_view.ui.removeDCOffsetCheckBox.setChecked(False)
    app.processEvents()

    controller.app_view.ui.actionReset_protocol.trigger()
    controller.app_view.ui.actionReset_filter.trigger()
    app.processEvents()

    assert (
        controller.protocol_view.ui.positiveChannelComboBox.currentIndex()
        == DEFAULT_PROTOCOL_CONFIG.positive_channel
    )
    assert (
        controller.protocol_view.ui.negativeChannelComboBox.currentIndex()
        == DEFAULT_PROTOCOL_CONFIG.negative_channel
    )
    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.isChecked()
    ] == DEFAULT_PROTOCOL_CONFIG.selected_pins
    assert (
        controller.protocol_view.ui.sampleRateDividerSpinBox.value()
        == DEFAULT_PROTOCOL_CONFIG.sample_rate_divider
    )
    assert (
        controller.overview_view.ui.doubleSpinBox.value()
        == DEFAULT_FILTER_CONFIG.low_pass_cutoff_hz
    )
    assert (
        controller.overview_view.ui.suppress50HzCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.suppress_50hz
    )
    assert (
        controller.overview_view.ui.removeDCOffsetCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.remove_dc_offset
    )

    controller.app_view.close()
    app.processEvents()


def test_reset_protocol_restores_pins_after_bulk_pin_edit():
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    select_all_button = controller.protocol_view.findChild(
        QPushButton, "selectAllPinsButton"
    )

    select_all_button.click()
    app.processEvents()

    assert controller.app_model.protocol_config.selected_pins == list(range(1, 17))

    controller.app_view.ui.actionReset_protocol.trigger()
    app.processEvents()

    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.isChecked()
    ] == DEFAULT_PROTOCOL_CONFIG.selected_pins

    controller.app_view.close()
    app.processEvents()


class FakeSettings:
    def __init__(self, stored_font_size=10):
        self.stored_font_size = stored_font_size
        self.values = {}

    def value(self, key, default=None, type=None):
        if key == "ui/font_size":
            return self.stored_font_size

        return default

    def setValue(self, key, value):
        self.values[key] = value


def test_restore_preferences_updates_font_size_spinbox_and_app_font():
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    controller.settings = FakeSettings(stored_font_size=13)

    controller.restore_preferences()

    assert controller.preferences_view.font_size() == 13
    assert app.font().pointSize() == 13

    controller.app_view.close()
    app.processEvents()


def test_preferences_font_size_spinbox_applies_and_persists_size():
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    fake_settings = FakeSettings()
    controller.settings = fake_settings
    controller.preferences_view.set_font_size(10)

    controller.preferences_view.ui.fontSizeSpinBox.stepUp()
    app.processEvents()

    assert controller.preferences_view.font_size() == 11
    assert app.font().pointSize() == 11
    assert fake_settings.values["ui/font_size"] == 11

    controller.preferences_view.ui.fontSizeSpinBox.stepDown()
    app.processEvents()

    assert controller.preferences_view.font_size() == 10
    assert app.font().pointSize() == 10
    assert fake_settings.values["ui/font_size"] == 10

    controller.app_view.close()
    app.processEvents()
