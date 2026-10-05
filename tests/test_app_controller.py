import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from app.app_controller import AppController
from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.acquisition.protocol_view import PinStateButton
from app.feature.filter.filter_config import FilterConfig
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.shared import data_dialog, data_io
from app.shared.constants import (
    DEFAULT_FILTER_CONFIG,
    DEFAULT_PROTOCOL_CONFIG,
    DEFAULT_STIMULUS_CONFIG,
    TITLE_LABEL_POINT_SIZE_INCREASE,
)


@pytest.mark.parametrize("confirm", [False, True])
def test_new_experiment_requires_confirmation(monkeypatch, confirm):
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    model = controller.app_model
    model.update_stim_config(StimulusConfig(0.1, 1.5, [], n_steps=2))
    model.update_protocol_config(ProtocolConfig(2, 3, [5], 4))
    model.update_filter_config(FilterConfig(250.0, False, False))
    data = pd.DataFrame({"t_(s)": [0.0, 0.001], "pin1": [0.1, 0.2]})
    model.update_raw_data(data)
    model.experiment_metadata = {"run": 3}
    original_state = model.export_state()
    dialogs = []

    def answer(dialog):
        dialogs.append(dialog)
        assert model.export_state() == original_state
        assert model.raw_data_df is data
        assert dialog.defaultButton() == dialog.button(
            QMessageBox.StandardButton.Cancel
        )
        return (
            QMessageBox.StandardButton.Yes
            if confirm
            else QMessageBox.StandardButton.Cancel
        )

    monkeypatch.setattr(QMessageBox, "exec", answer)
    try:
        controller.app_view.ui.actionNew.trigger()
        assert len(dialogs) == 1
        if confirm:
            assert model.stim_config == DEFAULT_STIMULUS_CONFIG
            assert model.protocol_config == DEFAULT_PROTOCOL_CONFIG
            assert model.filter_config == DEFAULT_FILTER_CONFIG
            assert model.raw_data_df is None
            assert model.filtered_data_df is None
            assert model.experiment_metadata == {}
        else:
            assert model.export_state() == original_state
            assert model.raw_data_df is data
            assert model.experiment_metadata == {"run": 3}
    finally:
        controller.app_view.close()
        app.processEvents()


@pytest.mark.parametrize(
    "action_name", ["actionReset_stimulus", "actionReset_protocol", "actionClear_data"]
)
def test_cancel_edit_action_preserves_state(monkeypatch, action_name):
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    model = controller.app_model
    model.update_stim_config(StimulusConfig(0.1, 1.5, [], n_steps=2))
    model.update_protocol_config(ProtocolConfig(2, 3, [5], 4))
    model.update_filter_config(FilterConfig(250.0, False, False))
    data = pd.DataFrame({"t_(s)": [0.0, 0.001], "pin1": [0.1, 0.2]})
    model.update_raw_data(data)
    model.experiment_metadata = {"run": 3}
    original_state = model.export_state()
    dialogs = []

    def cancel(dialog):
        dialogs.append(dialog.icon())
        assert model.export_state() == original_state
        assert model.raw_data_df is data
        assert dialog.defaultButton() == dialog.button(
            QMessageBox.StandardButton.Cancel
        )
        return QMessageBox.StandardButton.Cancel

    monkeypatch.setattr(QMessageBox, "exec", cancel)
    try:
        getattr(controller.app_view.ui, action_name).trigger()
        assert dialogs == [QMessageBox.Icon.Question]
        assert model.export_state() == original_state
        assert model.raw_data_df is data
        assert model.filtered_data_df is data
        assert model.experiment_metadata == {"run": 3}
    finally:
        controller.app_view.close()
        app.processEvents()


def test_clear_data_preserves_settings(reset_messages):
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    model = controller.app_model
    model.update_raw_data(pd.DataFrame({"t_(s)": [0.0, 0.001], "pin1": [0.1, 0.2]}))
    model.experiment_metadata = {"run": 3}
    model.experiment_config = {"name": "recording"}
    state = model.export_state()
    try:
        controller.app_view.ui.actionClear_data.trigger()
        assert model.raw_data_df is None
        assert model.filtered_data_df is None
        assert model.experiment_metadata == {}
        assert model.experiment_config == {}
        assert model.export_state() == state
        assert controller.analyze_io_view.curve.getData() == (None, None)
        assert reset_messages == [("Clear complete", "Data has been cleared.")]
    finally:
        controller.app_view.close()
        app.processEvents()


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


def test_save_protocol_action_is_connected(monkeypatch):
    app = QApplication.instance() or QApplication([])
    save_requests = []

    monkeypatch.setattr(
        AppController,
        "save_protocol_state",
        lambda self: save_requests.append("protocol"),
    )

    controller = AppController()
    controller.app_view.ui.actionSave_protocol.trigger()
    app.processEvents()

    assert save_requests == ["protocol"]
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

    assert writes[0][0].endswith("test.protocol.json")
    assert set(writes[0][1]) == {"protocol_config", "filter_config"}
    assert len(writes) == 1

    controller.app_view.close()
    app.processEvents()


@pytest.mark.parametrize("file_kind", ["combined", "legacy", "unwrapped"])
def test_load_protocol_restores_settings(monkeypatch, file_kind):
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    state = controller.app_model.export_state()
    state["protocol_config"]["sample_rate_divider"] = 8
    state["filter_config"]["low_pass_cutoff_hz"] = 250.0
    expected_filter = controller.app_model.filter_config
    if file_kind == "combined":
        payload = {key: state[key] for key in ("protocol_config", "filter_config")}
        expected_filter = FilterConfig(**state["filter_config"])
    elif file_kind == "legacy":
        payload = {"protocol_config": state["protocol_config"]}
    else:
        payload = state["protocol_config"]

    monkeypatch.setattr(
        data_dialog, "show_load_json_dialog", lambda: "test.protocol.json"
    )
    monkeypatch.setattr(data_io, "read_metadata", lambda filename: payload)
    try:
        controller.app_view.ui.actionLoad_protocol.trigger()
        assert controller.app_model.protocol_config.sample_rate_divider == 8
        assert controller.protocol_view.ui.sampleRateDividerComboBox.currentData() == 8
        assert controller.app_model.filter_config == expected_filter
        assert (
            controller.protocol_view.ui.lowPassHzDoubleSpinBox.value()
            == expected_filter.low_pass_cutoff_hz
        )
    finally:
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

    controller = AppController()
    controller.app_view.ui.actionReset_stimulus.trigger()
    controller.app_view.ui.actionReset_protocol.trigger()
    app.processEvents()

    assert reset_requests == ["stimulus", "protocol"]
    controller.app_view.close()
    app.processEvents()


@pytest.fixture
def reset_messages(monkeypatch):
    """Capture reset confirmations without blocking tests on a modal dialog."""
    messages = []

    def record_message(dialog):
        if dialog.icon() == QMessageBox.Icon.Question:
            return QMessageBox.StandardButton.Yes
        messages.append((dialog.windowTitle(), dialog.text()))
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "exec", record_message)
    return messages


def test_reset_config_actions_restore_default_configs(reset_messages):
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
    app.processEvents()

    assert reset_messages == [
        ("Reset complete", "Stimulus has been reset."),
        ("Reset complete", "Protocol has been reset."),
    ]
    assert controller.app_model.stim_config == DEFAULT_STIMULUS_CONFIG
    assert controller.app_model.stim_config is not DEFAULT_STIMULUS_CONFIG
    assert controller.app_model.protocol_config == DEFAULT_PROTOCOL_CONFIG
    assert controller.app_model.protocol_config is not DEFAULT_PROTOCOL_CONFIG
    assert controller.app_model.filter_config == DEFAULT_FILTER_CONFIG
    assert controller.app_model.filter_config is not DEFAULT_FILTER_CONFIG
    controller.protocol_view.ui.lowPassHzDoubleSpinBox.setValue(123.0)
    assert controller.app_model.filter_config == DEFAULT_FILTER_CONFIG
    controller.filter_controller.update_ui_from_model()
    protocol_view_config = controller.protocol_view.to_config()
    assert (
        protocol_view_config.positive_channel
        == DEFAULT_PROTOCOL_CONFIG.positive_channel
    )
    assert (
        protocol_view_config.negative_channel
        == DEFAULT_PROTOCOL_CONFIG.negative_channel
    )
    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.pin_state == PinStateButton.GREEN_STATE
    ] == DEFAULT_PROTOCOL_CONFIG.selected_pins
    assert (
        controller.protocol_view.ui.sampleRateDividerComboBox.currentData()
        == DEFAULT_PROTOCOL_CONFIG.sample_rate_divider
    )
    assert (
        controller.protocol_view.ui.lowPassHzDoubleSpinBox.value()
        == DEFAULT_FILTER_CONFIG.low_pass_cutoff_hz
    )
    assert (
        controller.protocol_view.ui.suppress50HzCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.suppress_50hz
    )
    assert (
        controller.protocol_view.ui.removeDCOffsetCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.remove_dc_offset
    )

    controller.app_view.close()
    app.processEvents()


def test_reset_config_actions_restore_ui_after_ui_edits(reset_messages):
    app = QApplication.instance() or QApplication([])
    controller = AppController()

    controller.protocol_view.pinButtons[0].setChecked(True)
    controller.protocol_view.pinButtons[-1].setChecked(False)
    controller.protocol_view.ui.sampleRateDividerComboBox.setCurrentIndex(2)
    controller.protocol_view.ui.lowPassHzDoubleSpinBox.setValue(123.0)
    controller.protocol_view.ui.suppress50HzCheckBox.setChecked(False)
    controller.protocol_view.ui.removeDCOffsetCheckBox.setChecked(False)
    app.processEvents()

    controller.app_view.ui.actionReset_protocol.trigger()
    app.processEvents()

    protocol_view_config = controller.protocol_view.to_config()
    assert (
        protocol_view_config.positive_channel
        == DEFAULT_PROTOCOL_CONFIG.positive_channel
    )
    assert (
        protocol_view_config.negative_channel
        == DEFAULT_PROTOCOL_CONFIG.negative_channel
    )
    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.pin_state == PinStateButton.GREEN_STATE
    ] == DEFAULT_PROTOCOL_CONFIG.selected_pins
    assert (
        controller.protocol_view.ui.sampleRateDividerComboBox.currentData()
        == DEFAULT_PROTOCOL_CONFIG.sample_rate_divider
    )
    assert (
        controller.protocol_view.ui.lowPassHzDoubleSpinBox.value()
        == DEFAULT_FILTER_CONFIG.low_pass_cutoff_hz
    )
    assert (
        controller.protocol_view.ui.suppress50HzCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.suppress_50hz
    )
    assert (
        controller.protocol_view.ui.removeDCOffsetCheckBox.isChecked()
        == DEFAULT_FILTER_CONFIG.remove_dc_offset
    )

    controller.app_view.close()
    app.processEvents()


def test_reset_protocol_restores_pins_after_bulk_pin_edit(reset_messages):
    app = QApplication.instance() or QApplication([])
    controller = AppController()
    deselect_all_button = controller.protocol_view.findChild(
        QPushButton, "deselectAllPinsButton"
    )

    deselect_all_button.click()
    app.processEvents()

    assert controller.app_model.protocol_config.selected_pins == []

    controller.app_view.ui.actionReset_protocol.trigger()
    app.processEvents()

    assert [
        index
        for index, button in enumerate(controller.protocol_view.pinButtons, start=1)
        if button.pin_state == PinStateButton.GREEN_STATE
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
    assert controller.app_view.ui.tabWidget.tabBar().font().pointSize() == 13
    assert (
        controller.stimulus_view.ui.title_stimulus.font().pointSize()
        == 13 + TITLE_LABEL_POINT_SIZE_INCREASE
    )

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
    assert controller.app_view.ui.tabWidget.tabBar().font().pointSize() == 11
    assert (
        controller.protocol_view.ui.title_controls.font().pointSize()
        == 11 + TITLE_LABEL_POINT_SIZE_INCREASE
    )
    assert fake_settings.values["ui/font_size"] == 11

    controller.preferences_view.ui.fontSizeSpinBox.stepDown()
    app.processEvents()

    assert controller.preferences_view.font_size() == 10
    assert app.font().pointSize() == 10
    assert controller.app_view.ui.tabWidget.tabBar().font().pointSize() == 10
    assert (
        controller.protocol_view.ui.title_controls.font().pointSize()
        == 10 + TITLE_LABEL_POINT_SIZE_INCREASE
    )
    assert fake_settings.values["ui/font_size"] == 10

    controller.app_view.close()
    app.processEvents()
