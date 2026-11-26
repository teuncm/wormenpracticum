import pyqtgraph as pg
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QCursor, QPainterPath
from PySide6.QtWidgets import (
    QDialog,
    QSizePolicy,
    QTabBar,
)

from app.feature.stimulus.pulse_tab_view import PulseTabView
from app.shared.constants import (
    DEFAULT_DUR_S,
    DEFAULT_PULSE_GAP_S,
    DOUBLE_SPIN_STEP_S,
    SEGMENT_VIEW_STIMULUS_HIGHLIGHT_DEFAULT,
)
from app.shared.view_helpers import (
    create_guide_line,
    create_plot_widget,
    double_spin_helper,
    setup_ui_custom,
)
from app.ui.generated.stimulus_window import Ui_StimulusWindow


class PulseTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        return QSize(
            size.width(),
            size.height() + 15,
        )


class StimulusPreviewViewBox(pg.ViewBox):
    """Allow vertical wheel zoom while reserving plot drags for pulse handles."""

    pulse_clicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.pulse_intervals: list[tuple[float, float]] = []
        self.setAcceptHoverEvents(True)

    def _pulse_at(self, scene_position: QPointF) -> int | None:
        """Find the selectable pulse at this time, regardless of voltage."""
        time_s = self.mapSceneToView(scene_position).x()
        # Later pulses overwrite earlier ones where their samples overlap.
        for index in reversed(range(len(self.pulse_intervals))):
            start_s, end_s = self.pulse_intervals[index]
            if start_s <= time_s < end_s:
                return index
        return None

    def hoverMoveEvent(self, event):
        if self._pulse_at(event.scenePos()) is None:
            self.unsetCursor()
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().hoverMoveEvent(event)

    def mouseClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            event.accept()
            index = self._pulse_at(event.scenePos())
            if index is not None:
                self.pulse_clicked.emit(index)
        else:
            super().mouseClickEvent(event)

    def wheelEvent(self, event, axis=None):
        if axis == pg.ViewBox.XAxis or not self.mouseEnabled()[1]:
            event.ignore()
            return

        # Keep pyqtgraph's wheel sensitivity and anchor scaling to the zero line.
        factor = 1.02 ** (event.delta() * self.state["wheelScaleFactor"])
        self.scaleBy(y=factor, center=(0, 0))
        event.accept()
        self.sigRangeChangedManually.emit([False, True])

    def mouseDragEvent(self, event, axis=None):
        event.ignore()


class PulseHandle(pg.TargetItem):
    """Report drag coordinates and let the preview place the handle after rounding."""

    dragged = Signal(QPointF)

    def __init__(self, cursor: Qt.CursorShape, **kwargs):
        super().__init__(**kwargs)
        self.setCursor(cursor)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

    def shape(self) -> QPainterPath:
        """Use a 24-pixel grab area at every zoom level."""
        transform = self.deviceTransform_()
        if transform is None:
            return super().shape()
        inverse, invertible = transform.inverted()
        if not invertible:
            return super().shape()
        hitbox = QPainterPath()
        hitbox.addEllipse(transform.map(QPointF()), 12, 12)
        return inverse.map(hitbox)

    def paint(self, painter, *_):
        # TargetItem normally paints its hitbox. Paint only the original symbol.
        painter.setPen(self.currentPen)
        painter.setBrush(self.currentBrush)
        painter.drawPath(super().shape())

    def mousePressEvent(self, event):
        # Accept the press so Qt keeps delivering moves and the cursor during the drag.
        event.accept()
        self.symbolOffset = self.pos() - self.mapToView(event.pos())
        self.moving = True

    def mouseMoveEvent(self, event):
        if not self.moving:
            return
        self.dragged.emit(self.symbolOffset + self.mapToView(event.pos()))

    def mouseReleaseEvent(self, event):
        if self.moving:
            self.moving = False
            self.sigPositionChangeFinished.emit(self)


class StimulusView(QDialog):
    stimulusChanged = Signal()
    stepChanged = Signal()
    stimulusHighlightChanged = Signal(bool)
    voltageBoundaryChanged = Signal(bool)
    previewPulseClicked = Signal(int)

    def __init__(self):
        super().__init__()

        self.ui = Ui_StimulusWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.setup_tabs()
        self.setup_widgets()
        self.connect_data_signals()

        self.stimulusChanged.emit()

    def connect_data_signals(self):

        self.ui.nSpinBox.valueChanged.connect(self.stimulusChanged)
        self.ui.stepSlider.valueChanged.connect(self.stepChanged)
        self.ui.durSpinBox.valueChanged.connect(self.stimulusChanged)
        self.ui.highlight_selected_pulse_checkbox.toggled.connect(
            self.stimulusHighlightChanged.emit
        )
        self.ui.show_voltage_boundary_checkbox.toggled.connect(
            self.voltageBoundaryChanged.emit
        )

        self.stimulusHighlightChanged.emit(
            self.ui.highlight_selected_pulse_checkbox.isChecked()
        )

    def setup_widgets(self):
        self.ui.highlight_selected_pulse_checkbox.setChecked(
            SEGMENT_VIEW_STIMULUS_HIGHLIGHT_DEFAULT
        )

        self.preview_view_box = StimulusPreviewViewBox()
        self.preview_view_box.pulse_clicked.connect(self.previewPulseClicked)
        frame, plot = create_plot_widget(
            x_label="Time",
            x_units="ms",
            y_label="Voltage",
            y_units="V",
            view_box=self.preview_view_box,
        )
        plot.setMouseEnabled(x=False, y=True)
        # Display milliseconds while keeping waveform coordinates in seconds.
        time_axis = plot.getAxis("bottom")
        time_axis.enableAutoSIPrefix(False)
        time_axis.setScale(1000)
        # Reserve room for signed tick labels so vertical zoom cannot move the plot sideways.
        tick_label_width = plot.fontMetrics().horizontalAdvance("-000.000")
        plot.getAxis("left").setWidth(tick_label_width + 12)
        self.ui.stepSlider.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.ui.waveformLayout.addWidget(frame)
        self.ui.rightLayout.setStretchFactor(self.ui.waveformLayout, 1)
        self.plotWidget = plot
        self.start_handle = PulseHandle(
            Qt.CursorShape.SizeAllCursor, size=13, symbol="o", pen="b", brush="w"
        )
        self.end_handle = PulseHandle(
            Qt.CursorShape.SizeHorCursor, size=12, symbol="s", pen="b", brush="w"
        )
        for handle, tooltip in (
            (self.start_handle, "Drag to change pulse start and amplitude"),
            (self.end_handle, "Drag left or right to change pulse duration"),
        ):
            handle.setToolTip(tooltip)
            handle.setZValue(10)
            plot.addItem(handle, ignoreBounds=True)
            handle.hide()

        double_spin_helper(
            self.ui.durSpinBox,
            default_val=DEFAULT_DUR_S,
            min_val=0.0001,
            max_val=1,
            step=DOUBLE_SPIN_STEP_S,
        )

    def setup_tabs(self):
        self.ui.segmentTabWidget.setTabBar(PulseTabBar())
        self.ui.segmentTabWidget.setTabsClosable(True)
        self.ui.segmentTabWidget.tabCloseRequested.connect(self.handle_close_tab)
        self.ui.segmentTabWidget.setMovable(True)
        tab_bar = self.ui.segmentTabWidget.tabBar()
        tab_bar.setUsesScrollButtons(True)
        tab_bar.tabMoved.connect(self.handle_move_tab)
        self.ui.segmentTabWidget.currentChanged.connect(self.renumber_tabs)

        # Add base segment tab.
        self.add_segment_tab()

        self.ui.add_pulse_button.clicked.connect(self.add_segment_tab)

        self.ui.segmentTabWidget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )

    def renumber_tabs(self):
        for i in range(self.ui.segmentTabWidget.count()):
            self.ui.segmentTabWidget.setTabText(i, f"Pulse {i + 1}")

        self.stimulusChanged.emit()
        self.stepChanged.emit()

    def handle_move_tab(self, *_):
        self.renumber_tabs()

    def handle_close_tab(self, index):
        self.ui.segmentTabWidget.removeTab(index)
        self.renumber_tabs()

    def add_segment_tab(self):
        """Add a pulse after the latest endpoint, keeping a gap between pulses."""
        segment = PulseTabView()

        tabs = self.ui.segmentTabWidget
        if tabs.count():
            # Tabs can be reordered, so find the last pulse in time.
            latest_end_s = 0.0
            for i in range(tabs.count()):
                widget = tabs.widget(i)
                if not isinstance(widget, PulseTabView):
                    continue
                spinboxes = widget.spinboxes
                end_s = spinboxes["start_s"].value() + spinboxes["dur_s"].value()
                latest_end_s = max(latest_end_s, end_s)

            segment.spinboxes["start_s"].setValue(latest_end_s + DEFAULT_PULSE_GAP_S)

        index = tabs.addTab(segment, "")
        tabs.setCurrentIndex(index)

        segment.segmentChanged.connect(self.stimulusChanged)
        self.renumber_tabs()

    def update_step_slider(self, n_steps: int) -> None:
        """Update the slider range before the controller redraws the preview."""
        self.ui.stepSlider.setMaximum(n_steps - 1)

    def show_step_position(self, step: int, n_steps: int) -> None:
        """Display the one-based position of the preview within the sequence."""
        self.ui.stimulusPositionLabel.setText(f"Stimulus {step + 1} of {n_steps}")

    def clear_plot(self):
        # Keep the handle items attached so the scene can finish an active drag.
        for item in list(self.plotWidget.getPlotItem().items):
            if item not in (self.start_handle, self.end_handle):
                self.plotWidget.removeItem(item)

    def position_pulse_handles(
        self, start_s: float, end_s: float, top_v: float
    ) -> None:
        """Place the amplitude handle at the pulse level and the duration handle at zero."""
        self.start_handle.setPos(start_s, top_v)
        self.start_handle.show()
        self.show_duration_handle(end_s)

    def show_duration_handle(self, end_s: float) -> None:
        """Expose the pulse endpoint on the baseline, even for a collapsed pulse."""
        self.end_handle.setPos(end_s, 0.0)
        self.end_handle.show()

    def hide_pulse_handles(self) -> None:
        for handle in (self.start_handle, self.end_handle):
            if not handle.moving:
                handle.hide()

    def draw_zero_line(self):
        self.plotWidget.addItem(
            create_guide_line(
                0, 0, color="k", width=1, style=Qt.PenStyle.SolidLine, alpha=30
            )
        )

    def update_train_plot(self, plot_data, color, width=1):
        if plot_data is not None:
            time_points, voltage_points = plot_data
            self.plotWidget.plot(
                time_points,
                voltage_points,
                pen=pg.mkPen(color=color, width=width),
                name="Stimulus",
            )

    def draw_segment_bounds(self, start_s: float, end_s: float) -> None:
        """Mark the highlighted pulse's visible start and end."""
        for boundary in (start_s, end_s):
            self.plotWidget.addItem(create_guide_line(boundary, 90, color="b"))

    def draw_voltage_limit(self, limit_v):
        self.plotWidget.addItem(
            create_guide_line(
                limit_v, 0, color="r", style=Qt.PenStyle.DashLine, alpha=150
            )
        )
        self.plotWidget.addItem(
            create_guide_line(
                -limit_v,
                0,
                color="r",
                style=Qt.PenStyle.DashLine,
                alpha=150,
            )
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.stimulusChanged.emit()
