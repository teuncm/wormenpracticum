import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.app_controller import AppController


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
