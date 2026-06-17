import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.app_controller import AppController
from app.shared import data_dialog, data_io


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
