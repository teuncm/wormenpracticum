import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.analysis.analyze_io_controller import AnalyzeIOController
from app.feature.analysis.analyze_view_io import AnalyzeIOView


@pytest.fixture
def io_analysis():
    """Create the IO model, view, and controller without requiring a display."""
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = AnalyzeIOView()
    controller = AnalyzeIOController(model, view)
    yield model, view, controller
    view.close()
    view.deleteLater()
    app.processEvents()


def test_io_uses_filtered_sequence_and_switches_channels(io_analysis):
    """Display all ten received stimuli and select channels from filtered data."""
    model, view, _ = io_analysis
    times = np.arange(100) / 10
    raw = pd.DataFrame({"t_(s)": times, "ai0_(V)": times, "ai1_(V)": -times})
    model.update_raw_data(raw)
    filtered = raw.copy()
    filtered["ai0_(V)"] = np.repeat(np.arange(10), 10)
    filtered["ai1_(V)"] = filtered["ai0_(V)"] * -0.5
    model.update_filtered_data(filtered)

    x, y = view.curve.getData()
    np.testing.assert_array_equal(x, times)
    np.testing.assert_array_equal(y, filtered["ai0_(V)"])
    assert view.ui.channelSlider.maximum() == 2
    assert view.ui.channelSlider.isEnabled()

    view.ui.channelSlider.setValue(2)
    np.testing.assert_array_equal(view.curve.getData()[1], filtered["ai1_(V)"])
    assert view.ui.channelLabel.text() == "Channel 02: ai1_(V)"

    # Refreshing a filter must preserve the selected channel and update its trace.
    filtered = filtered.copy()
    filtered["ai1_(V)"] *= 2
    model.update_filtered_data(filtered)
    assert view.ui.channelSlider.value() == 2
    np.testing.assert_array_equal(view.curve.getData()[1], filtered["ai1_(V)"])


def test_io_handles_missing_data_and_replacement_channels(io_analysis):
    """Clear stale traces and safely adjust the slider when recordings change."""
    model, view, _ = io_analysis
    assert not view.ui.channelSlider.isEnabled()
    assert view.curve.getData()[0] is None

    model.update_filtered_data(
        pd.DataFrame(
            {
                "t_(s)": [0.0, 0.1],
                "ai0_(V)": [1.0, 2.0],
                "ai1_(V)": [3.0, 4.0],
            }
        )
    )
    view.ui.channelSlider.setValue(2)
    model.update_filtered_data(
        pd.DataFrame(
            {
                "t_(s)": [0.0, 0.1],
                "ai0_(V)": [5.0, 6.0],
            }
        )
    )
    assert view.ui.channelSlider.value() == 1
    assert not view.ui.channelSlider.isEnabled()
    np.testing.assert_array_equal(view.curve.getData()[1], [5.0, 6.0])

    for data in (pd.DataFrame(), pd.DataFrame({"ai0_(V)": [1.0]})):
        model.update_filtered_data(data)
        assert view.curve.getData()[0] is None
        assert view.ui.channelLabel.text() == "Channel: no data"
