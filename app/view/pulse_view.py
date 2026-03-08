import pyqtgraph as pg
from app.view.pulse_segment import PulseSegmentWidget
from app.window.ui_pulse_window import Ui_PulseWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QVBoxLayout,
)


class PulseView(QDialog):
    pulseChanged = Signal()
    stepChanged = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_PulseWindow()
        self.ui.setupUi(self)

        # Configure tab management.
        self.ui.segmentTabWidget.setTabsClosable(True)
        self.ui.segmentTabWidget.tabCloseRequested.connect(self.handle_close_tab)
        self.ui.segmentTabWidget.setMovable(True)
        self.ui.segmentTabWidget.tabBar().setUsesScrollButtons(True)
        self.ui.segmentTabWidget.tabBar().tabMoved.connect(self.handle_move_tab)
        self.ui.segmentTabWidget.currentChanged.connect(self.renumber_tabs)

        # Add base segment tab.
        self.add_segment_tab()

        # Add new tab button and anchor it to the top right corner of the tab widget.
        new_segment_button = QPushButton("+")
        new_segment_button.setFixedWidth(25)
        new_segment_button.clicked.connect(self.add_segment_tab)
        self.ui.segmentTabWidget.setCornerWidget(
            new_segment_button, Qt.Corner.TopRightCorner
        )
        new_segment_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Create plot widget for pulse visualization.
        self.plotWidget = pg.PlotWidget()
        layout = QVBoxLayout(self.ui.pulseContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotWidget)

        self.plotWidget.setTitle("Impulse")
        self.plotWidget.setLabel("left", "Voltage", units="V")
        self.plotWidget.setLabel("bottom", "Time", units="s")
        self.plotWidget.setMouseEnabled(x=False, y=False)

        self.ui.nSpinBox.valueChanged.connect(self.pulseChanged)
        self.ui.stepSlider.valueChanged.connect(self.stepChanged)

        self.pulseChanged.emit()

    def renumber_tabs(self):
        for i in range(self.ui.segmentTabWidget.count()):
            self.ui.segmentTabWidget.setTabText(i, f"{i + 1}")

        self.pulseChanged.emit()
        self.stepChanged.emit()

    def handle_move_tab(self, *_):
        self.renumber_tabs()

    def handle_close_tab(self, index):
        # Keep at least one segment tab open.
        if self.ui.segmentTabWidget.count() <= 1:
            return

        self.ui.segmentTabWidget.removeTab(index)
        self.renumber_tabs()

    def add_segment_tab(self):
        segment = PulseSegmentWidget()

        index = self.ui.segmentTabWidget.addTab(segment, "")
        self.ui.segmentTabWidget.setCurrentIndex(index)

        segment.segmentChanged.connect(self.pulseChanged)
        self.renumber_tabs()

    def update_step_slider(self, n_steps):
        max_idx = n_steps - 1
        self.ui.stepSlider.setMaximum(max_idx)

        self.ui.stepSlider.setValue(max_idx)

        # Emit stepChanged to update the plot.
        self.stepChanged.emit()

    def clear_plot(self):
        self.plotWidget.clear()

    def update_pulse_plot(self, plot_data, color, width=2):
        if plot_data is not None:
            time_points, voltage_points = plot_data
            self.plotWidget.plot(
                time_points,
                voltage_points,
                pen=pg.mkPen(color=color, width=width),
                name="Pulse",
            )

    def update_pulse_bounds(self, lt, rt, tp, bt):
        guide_color = "b"

        left = pg.InfiniteLine(
            pos=lt,
            angle=90,
            pen=pg.mkPen(
                color=guide_color,
                width=1,
                style=Qt.PenStyle.DotLine,
                alpha=0.3,
            ),
        )

        right = pg.InfiniteLine(
            pos=rt,
            angle=90,
            pen=pg.mkPen(
                color=guide_color,
                width=1,
                style=Qt.PenStyle.DotLine,
                alpha=0.3,
            ),
        )

        top = pg.InfiniteLine(
            pos=tp,
            angle=0,
            pen=pg.mkPen(
                color=guide_color,
                width=1,
                style=Qt.PenStyle.DotLine,
                alpha=0.3,
            ),
        )

        bottom = pg.InfiniteLine(
            pos=bt,
            angle=0,
            pen=pg.mkPen(
                color=guide_color,
                width=1,
                style=Qt.PenStyle.DotLine,
                alpha=0.3,
            ),
        )

        left.setZValue(-10)
        right.setZValue(-10)
        top.setZValue(-10)
        bottom.setZValue(-10)

        self.plotWidget.addItem(left)
        self.plotWidget.addItem(right)
        self.plotWidget.addItem(top)
        self.plotWidget.addItem(bottom)

    def showEvent(self, event):
        super().showEvent(event)
        self.pulseChanged.emit()
