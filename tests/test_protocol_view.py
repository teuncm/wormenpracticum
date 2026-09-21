import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QPushButton

from app.app_model import AppModel
from app.feature.acquisition.protocol_controller import ProtocolController
from app.feature.acquisition.protocol_view import PinStateButton, ProtocolView


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

        for name, color in (
            ("selectAllPinsButton", "#2f9e44"),
            ("deselectAllPinsButton", "gray"),
        ):
            view.findChild(QPushButton, name).click()
            app.processEvents()
            assert all(bar.opts["pen"].color() == pg.mkColor(color) for bar in bars)
            np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)

        # Model-driven refreshes must update colors as well as the buttons.
        view.pinButtons[0].set_pin_state(PinStateButton.BLUE_STATE)
        controller.update_ui_from_model()
        app.processEvents()
        assert bars[0].opts["pen"].color() == pg.mkColor("#2f9e44")
        np.testing.assert_allclose(view.plotWidget.viewRange(), original_range)
    finally:
        view.close()
        view.deleteLater()
        app.processEvents()
