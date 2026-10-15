import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.app_model import AppModel
from app.feature.analysis.analyze_view_yolo import AnalyzeYoloView
from app.feature.analysis.analyze_yolo_controller import AnalyzeYoloController
from app.feature.analysis.display_selection import parse_display_selection
from tools.worm_recording_gen import gen_dummy_recording


@pytest.fixture
def yolo_analysis():
    app = QApplication.instance() or QApplication([])
    model = AppModel()
    view = AnalyzeYoloView()
    controller = AnalyzeYoloController(model, view)
    yield model, view, controller
    view.close()
    view.deleteLater()
    app.processEvents()


def test_yolo_mouse_and_keyboard_cannot_change_plot_range(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 2, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.show()
    QApplication.instance().processEvents()
    plot = view.plot_widget
    view_box = plot.getViewBox()
    assert view_box.mouseEnabled() == [False, False]
    original_range = np.array(plot.viewRange())

    # Seed a zoom history so keyboard shortcuts would otherwise change the range.
    view_box.axHistory = [QRectF(0, -1, 0.01, 2), QRectF(0, -2, 0.02, 4)]
    view_box.axHistoryPointer = 1
    plot.scene().setFocusItem(view_box)
    for key in (Qt.Key.Key_Minus, Qt.Key.Key_Plus, Qt.Key.Key_Backspace):
        QTest.keyClick(plot, key)
        np.testing.assert_allclose(plot.viewRange(), original_range)

    viewport = plot.viewport()
    center = viewport.rect().center()
    for button in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
        QTest.mousePress(viewport, button, pos=center)
        QTest.mouseMove(viewport, center + QPoint(30, 20))
        QTest.mouseRelease(viewport, button, pos=center + QPoint(30, 20))
        np.testing.assert_allclose(plot.viewRange(), original_range)

    wheel = QWheelEvent(
        QPointF(center),
        QPointF(viewport.mapToGlobal(center)),
        QPoint(),
        QPoint(0, 120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(viewport, wheel)
    np.testing.assert_allclose(plot.viewRange(), original_range)


def test_yolo_amplitude_controls_total_span_and_keeps_lowest_pin_unshifted(
    yolo_analysis,
):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])

    view.ui.amplitudeSpinBox.setValue(8.0)

    assert len(view.curves) == len(view.pin_labels) == 16
    assert view.curves[0].getOriginalDataset()[1].tolist() == data["ai0_(V)"].tolist()
    assert view.curves[1].getOriginalDataset()[1].tolist() == pytest.approx(
        (data["ai1_(V)"] + 0.5).tolist()
    )
    assert view.plot_widget.viewRange()[1] == pytest.approx((-0.25, 7.75))
    lower = view.plot_widget.viewRange()[1][0]
    assert [
        (label.pos().y() - lower) / 8.0 for label in view.pin_labels
    ] == pytest.approx([(rank + 0.5) / 16 for rank in range(16)])

    view.plot_widget.setXRange(0.01, 0.03, padding=0)
    previous_x = view.plot_widget.viewRange()[0]
    view.ui.amplitudeSpinBox.setValue(12.0)
    assert view.plot_widget.viewRange()[0] == pytest.approx(previous_x)
    assert view.plot_widget.viewRange()[1] == pytest.approx((-0.375, 11.625))
    assert [label.pos().y() / 12.0 for label in view.pin_labels] == pytest.approx(
        [rank / 16 for rank in range(16)]
    )
    view.plot_widget.setRange(xRange=(0.01, 0.03), yRange=(-1, 1), padding=0)
    previous_range = view.plot_widget.viewRange()
    view.ui.minCheckBox.setChecked(False)
    view.ui.maxCheckBox.setChecked(False)
    current_range = view.plot_widget.viewRange()
    assert current_range[0] == pytest.approx(previous_range[0])
    assert current_range[1] == pytest.approx(previous_range[1])

    filtered = data.copy()
    filtered["ai1_(V)"] *= 2
    model.update_filtered_data(filtered)
    assert view.ui.amplitudeSpinBox.value() == 12.0
    assert view.curves[1].getOriginalDataset()[1] == pytest.approx(
        (filtered["ai1_(V)"] + 0.75).to_numpy()
    )


def test_yolo_uses_physical_pin_order_and_marker_offsets(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 1, 4)
    data = data[["t_(s)", "ai15_(V)", "ai0_(V)"]]
    metadata = payload["metadata"] | {"pin_channels": {"ai15_(V)": 16, "ai0_(V)": 1}}
    model.update_recording(data, metadata, payload["experiment_config"])
    view.ui.amplitudeSpinBox.setValue(4.0)

    assert [label.toPlainText() for label in view.pin_labels] == ["Pin 1", "Pin 16"]
    assert len(view.peak_markers.points()) == 4
    for point in view.peak_markers.points():
        offset = 0.0 if point.data()["pin"] == "Pin 1" else 2.0
        assert point.pos().y() == pytest.approx(point.data()["voltage_v"] + offset)
        assert f"{point.data()['voltage_v']:.6g} V" in view._peak_tooltip(
            point.pos().x(), point.pos().y(), point.data()
        )


def test_yolo_keeps_traces_without_valid_markers_and_clears(yolo_analysis):
    model, view, _ = yolo_analysis
    data, _ = gen_dummy_recording(0.02, 1, 4)
    data = data[["t_(s)", "ai0_(V)"]]
    data["ai0_(V)"] = np.nan
    model.update_recording(data, {"pin_channels": []}, {})

    assert len(view.curves) == 1
    assert len(view.peak_markers.points()) == 0
    assert not view.ui.minCheckBox.isEnabled()
    assert not view.ui.maxCheckBox.isEnabled()

    data, payload = gen_dummy_recording(0.02, 1, 4)
    data = data[["t_(s)", "ai0_(V)"]]
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.amplitudeSpinBox.setValue(6.0)
    assert len(view.curves) == 1
    assert view.plot_widget.viewRange()[1] == pytest.approx((-3.0, 3.0))

    model.clear_experiment_data()
    assert not view.curves
    assert not view.pin_labels
    assert len(view.peak_markers.points()) == 0


def test_yolo_selects_pins_and_stimuli_without_bridging_gaps(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])

    view.ui.pinsLineEdit.setText("2, 1")
    view._apply_pin_selection()
    view.ui.stimuliLineEdit.setText("3, 1")
    view._apply_stimulus_selection()

    assert [label.toPlainText() for label in view.pin_labels] == ["Pin 1", "Pin 2"]
    assert len(view.curves) == 2
    xs, ys = view.curves[0].getOriginalDataset()
    size = payload["metadata"]["stimulus_size_samples"]
    assert xs[:size].tolist() == data["t_(s)"].iloc[:size].tolist()
    assert np.isnan(xs[size]) and np.isnan(ys[size])
    assert xs[size + 1 :].tolist() == data["t_(s)"].iloc[2 * size :].tolist()
    assert [point.data()["number"] for point in view.peak_markers.points()] == [
        1,
        1,
        3,
        3,
        1,
        1,
        3,
        3,
    ]


@pytest.mark.parametrize(
    "selection, first, last", [("2", 2, 2), ("2-3", 2, 3), ("1,3", 1, 3), ("", 1, 4)]
)
def test_yolo_stimulus_selection_fits_selected_timespan(
    yolo_analysis, selection, first, last
):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 4, 4)
    data["t_(s)"] += 5.0
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    metadata = payload["metadata"]
    duration = metadata["stimulus_size_samples"] / metadata["sample_rate_hz"]
    start = 5.0 + (first - 1) * duration
    end = 5.0 + last * duration
    view.ui.stimuliLineEdit.setText(selection)
    view.ui.stimuliLineEdit.editingFinished.emit()
    lower, upper = view.plot_widget.viewRange()[0]
    assert start - (end - start) * 0.15 <= lower <= start
    assert end <= upper <= end + (end - start) * 0.05
    assert view.pin_labels[0].pos().x() == pytest.approx(start)

    filtered = data.copy()
    filtered["ai0_(V)"] *= 2
    model.update_filtered_data(filtered)
    assert view.plot_widget.viewRange()[0] == pytest.approx((lower, upper))


def test_yolo_selector_errors_keep_last_view_and_refresh_intersects(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    view.ui.pinsLineEdit.setText("1-2")
    view._apply_pin_selection()
    view.ui.stimuliLineEdit.setText("1,3")
    view._apply_stimulus_selection()
    previous_curve = view.curves[0]

    view.ui.pinsLineEdit.setText("1,,2")
    view._apply_pin_selection()
    assert view.curves[0] is previous_curve
    assert view.ui.selectionErrorLabel.text()

    shorter, shorter_payload = gen_dummy_recording(0.02, 1, 4)
    shorter = shorter[["t_(s)", "ai0_(V)"]]
    model.update_recording(
        shorter,
        {**shorter_payload["metadata"], "pin_channels": {"ai0_(V)": 1}},
        shorter_payload["experiment_config"],
    )
    assert len(view.curves) == 1
    assert [point.data()["number"] for point in view.peak_markers.points()] == [1, 1]


def test_display_selection_parser_handles_ranges_and_rejects_invalid_bounds():
    assert parse_display_selection(" 5-8, 1,3,3 ", range(1, 10)) == [1, 3, 5, 6, 7, 8]
    assert parse_display_selection("1-999999", [1, 3, 5], strict=False) == [1, 3, 5]
    with pytest.raises(ValueError, match="ascend"):
        parse_display_selection("8-5", range(1, 10))
    with pytest.raises(ValueError, match="available"):
        parse_display_selection("1,10", range(1, 10))


def test_yolo_region_bounds_filter_extrema_and_clicks_use_local_time(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    size = payload["metadata"]["stimulus_size_samples"]
    times = data["t_(s)"].to_numpy()
    data["ai0_(V)"] = 0.25
    for number in (1, 3):
        start = (number - 1) * size
        local_times = times[start : start + size] - times[start]
        in_region = np.flatnonzero((local_times >= 0.005) & (local_times <= 0.008))
        data.loc[data.index[start], "ai0_(V)"] = 100.0
        data.loc[data.index[start + in_region[0]], "ai0_(V)"] = -2.0
        data.loc[data.index[start + in_region[1]], "ai0_(V)"] = 3.0
    model.update_recording(
        data[["t_(s)", "ai0_(V)"]],
        {**payload["metadata"], "pin_channels": {"ai0_(V)": 1}},
        payload["experiment_config"],
    )
    view.ui.stimuliLineEdit.setText("1,3")
    view._apply_stimulus_selection()
    view.ui.detectionStartLineEdit.setText("5")
    view.ui.detectionEndLineEdit.setText("8")
    view._apply_detection_region()

    assert len(view.peak_markers.points()) == 4
    assert all(
        point.data()["voltage_v"] in (-2.0, 3.0) for point in view.peak_markers.points()
    )
    curve = view.curves[0]
    marker_count = len(view.peak_markers.points())
    view.plot_widget.setRange(
        xRange=(float(times[0]), float(times[-1])), yRange=(-1.0, 1.0), padding=0
    )
    previous_range = view.plot_widget.viewRange()
    view.ui.detectionStartLineEdit.setText("5.5")
    view._apply_detection_region()
    assert view.curves[0] is curve
    assert view.plot_widget.viewRange()[0] == pytest.approx(previous_range[0])
    assert view.plot_widget.viewRange()[1] == pytest.approx(previous_range[1])

    view.ui.detectionStartLineEdit.setText("9")
    view.ui.detectionEndLineEdit.setText("2")
    view._apply_detection_region()
    assert view.ui.regionErrorLabel.text()
    assert view.curves[0] is curve
    assert len(view.peak_markers.points()) == marker_count

    assert view._local_stimulus_time(float(times[0] + 0.006)) == pytest.approx(0.006)
    assert view._local_stimulus_time(float(times[size] + 0.006)) is None
    assert view._local_stimulus_time(float(times[2 * size] + 0.006)) == pytest.approx(
        0.006
    )

    class SceneClick:
        def __init__(self, button, timestamp, voltage):
            self._button = button
            self.timestamp = timestamp
            self.voltage = voltage

        def button(self):
            return self._button

        def scenePos(self):
            return (
                view.plot_widget.getPlotItem()
                .getViewBox()
                .mapViewToScene(QPointF(self.timestamp, self.voltage))
            )

    view.show()
    QApplication.instance().processEvents()
    before_click = view.ui.detectionStartLineEdit.text()
    gap_click = SceneClick(Qt.MouseButton.LeftButton, float(times[size] + 0.006), 0.0)
    view._set_region_from_click(gap_click)
    assert view.ui.detectionStartLineEdit.text() == before_click

    view.ui.detectionStartLineEdit.clear()
    view.ui.detectionEndLineEdit.clear()
    view._apply_detection_region()
    view._set_region_from_click(
        SceneClick(Qt.MouseButton.RightButton, float(times[2 * size] + 0.006), 0.0)
    )
    assert float(view.ui.detectionEndLineEdit.text()) == pytest.approx(6.0)

    view.plot_widget.setYRange(-3.0, 4.0, padding=0)
    marker = view.peak_markers.points()[0]
    view._set_region_from_click(
        SceneClick(
            Qt.MouseButton.LeftButton,
            float(marker.pos().x()),
            float(marker.pos().y()),
        )
    )
    assert view.ui.detectionStartLineEdit.text()

    # Use the injected peak's exact sample time for this inclusive one-sample region.
    peak_time_ms = float((times[in_region[1]] - times[0]) * 1000)
    bound_text = f"{peak_time_ms:.12g}"
    view.ui.detectionStartLineEdit.setText(bound_text)
    view.ui.detectionEndLineEdit.setText(bound_text)
    view._apply_detection_region()
    assert len(view.peak_markers.points()) == 4
    assert all(point.data()["voltage_v"] == 3.0 for point in view.peak_markers.points())

    view.ui.detectionStartLineEdit.setText("100000")
    view.ui.detectionEndLineEdit.setText("100001")
    view._apply_detection_region()
    assert len(view.peak_markers.points()) == 0


def test_yolo_guide_lines_repeat_per_stimulus_and_toggle_without_rescaling(
    yolo_analysis,
):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 3, 4)
    data["t_(s)"] += 5.0
    model.update_recording(data, payload["metadata"], payload["experiment_config"])
    size = payload["metadata"]["stimulus_size_samples"]
    starts = data["t_(s)"].iloc[::size].to_numpy()
    assert [line.value() for line in view.guide_lines["start"]] == pytest.approx(starts)
    assert len(view.guide_lines["lower"]) == len(view.guide_lines["upper"]) == 0

    view.ui.detectionStartLineEdit.setText("3")
    view.ui.detectionEndLineEdit.setText("8")
    view.ui.detectionEndLineEdit.editingFinished.emit()
    assert [line.value() for line in view.guide_lines["lower"]] == pytest.approx(
        starts + 0.003
    )
    assert [line.value() for line in view.guide_lines["upper"]] == pytest.approx(
        starts + 0.008
    )
    for kind, lines in view.guide_lines.items():
        assert all(line.pen.style() == Qt.PenStyle.DotLine for line in lines)
        if kind == "start":
            assert all(line.pen.color().name() == "#888888" for line in lines)

    curves = list(view.curves)
    view.plot_widget.setRange(xRange=(5.01, 5.04), yRange=(-0.5, 0.5), padding=0)
    previous_range = np.array(view.plot_widget.viewRange())
    for kind, checkbox in (
        ("lower", view.ui.showDetectionStartCheckBox),
        ("upper", view.ui.showDetectionEndCheckBox),
        ("start", view.ui.showStimulusStartsCheckBox),
    ):
        checkbox.setChecked(False)
        assert len(view.guide_lines[kind]) == 0
        assert view.curves == curves
        np.testing.assert_allclose(view.plot_widget.viewRange(), previous_range)
        checkbox.setChecked(True)
        assert len(view.guide_lines[kind]) == 3
        np.testing.assert_allclose(view.plot_widget.viewRange(), previous_range)

    view.ui.stimuliLineEdit.setText("1,3")
    view.ui.stimuliLineEdit.editingFinished.emit()
    assert [line.value() for line in view.guide_lines["start"]] == pytest.approx(
        starts[[0, 2]]
    )
    assert len(view.guide_lines["lower"]) == len(view.guide_lines["upper"]) == 2
    view.ui.detectionStartLineEdit.setText("4")
    view.ui.detectionStartLineEdit.editingFinished.emit()
    assert [line.value() for line in view.guide_lines["lower"]] == pytest.approx(
        starts[[0, 2]] + 0.004
    )

    # Invalid input retains the last valid bounds and their corresponding guides.
    view.ui.detectionStartLineEdit.setText("9")
    view.ui.detectionStartLineEdit.editingFinished.emit()
    assert [line.value() for line in view.guide_lines["lower"]] == pytest.approx(
        starts[[0, 2]] + 0.004
    )
    model.clear_experiment_data()
    assert all(len(lines) == 0 for lines in view.guide_lines.values())


def test_yolo_pin_subset_uses_lowest_displayed_pin_as_reference(yolo_analysis):
    model, view, _ = yolo_analysis
    data, payload = gen_dummy_recording(0.02, 2, 4)
    model.update_recording(data, payload["metadata"], payload["experiment_config"])

    view.ui.pinsLineEdit.setText("3-4")
    view._apply_pin_selection()

    assert [label.toPlainText() for label in view.pin_labels] == ["Pin 3", "Pin 4"]
    assert view.curves[0].getOriginalDataset()[1].tolist() == data["ai2_(V)"].tolist()
    assert "Voltage axis refers to Pin 3" in view.ui.recordingStatusLabel.text()
