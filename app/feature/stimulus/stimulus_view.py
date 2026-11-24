import pyqtgraph as pg
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QCursor
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
    """Allow wheel zoom while reserving plot drags for pulse handles."""

    def mouseDragEvent(self, event, axis=None):
        event.ignore()


class PulseHandle(pg.TargetItem):
    """Report drag coordinates and let the preview place the handle after rounding."""

    dragged = Signal(QPointF)

    def mouseDragEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        event.accept()
        if event.isStart():
            self.symbolOffset = self.pos() - self.mapToView(event.buttonDownPos())
            self.moving = True
        if not self.moving:
            return
        self.dragged.emit(self.symbolOffset + self.mapToView(event.pos()))
        if event.isFinish():
            self.moving = False
            self.sigPositionChangeFinished.emit(self)


class StimulusView(QDialog):
    stimulusChanged = Signal()
    stepChanged = Signal()
    stimulusHighlightChanged = Signal(bool)
    voltageBoundaryChanged = Signal(bool)

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

        frame, plot = create_plot_widget(
            x_label="Time",
            x_units="ms",
            y_label="Voltage",
            y_units="V",
            view_box=StimulusPreviewViewBox(),
        )
        plot.setMouseEnabled(x=True, y=True)
        # Display milliseconds while keeping waveform coordinates in seconds.
        time_axis = plot.getAxis("bottom")
        time_axis.enableAutoSIPrefix(False)
        time_axis.setScale(1000)
        self.ui.stepSlider.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.ui.waveformLayout.addWidget(frame)
        self.ui.rightLayout.setStretchFactor(self.ui.waveformLayout, 1)
        self.plotWidget = plot
        self.start_handle = PulseHandle(size=13, symbol="o", pen="b", brush="w")
        self.end_handle = PulseHandle(size=12, symbol="s", pen="b", brush="w")
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
        self, start_s: float, end_s: float, top_v: float, middle_v: float
    ) -> None:
        """Place the handles at the corners of the highlighted pulse."""
        self.start_handle.setPos(start_s, top_v)
        self.end_handle.setPos(end_s, middle_v)
        self.start_handle.show()
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
