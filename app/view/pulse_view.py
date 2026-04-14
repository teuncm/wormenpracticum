import pyqtgraph as pg
from app.constants import (
    DEFAULT_DUR_S,
    DEFAULT_LIMIT_V,
    SEGMENT_VIEW_MAX_V,
    SEGMENT_VIEW_PULSE_HIGHLIGHT_DEFAULT,
    SEGMENT_VIEW_STEP_S,
    SEGMENT_VIEW_STEP_V,
)
from app.view.pulse_segment import PulseSegmentWidget
from app.view.view_helpers import (
    create_guide_line,
    create_plot_widget,
    create_title,
    spin_value_helper,
)
from app.window.ui_pulse_window import Ui_PulseWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QPushButton,
    QSizePolicy,
)


class PulseView(QDialog):
    pulseChanged = Signal()
    stepChanged = Signal()
    pulseHighlightChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        self.ui = Ui_PulseWindow()
        self.ui.setupUi(self)

        self.setup_tabs()

        self.highlightPulseCheckbox = QCheckBox("Highlight selected pulse")
        self.highlightPulseCheckbox.setChecked(SEGMENT_VIEW_PULSE_HIGHLIGHT_DEFAULT)

        frame, plot = create_plot_widget(
            title="Stimulus",
            x_label="Time",
            x_units="s",
            y_label="Voltage",
            y_units="V",
        )

        # spacer(self.ui.horizontalLayout)
        self.ui.parameterLayout.insertWidget(0, create_title("Stimulus parameters"))
        self.ui.parameterLayout.insertWidget(
            self.ui.parameterLayout.indexOf(self.ui.segmentTabWidget),
            create_title("Pulse parameters"),
        )
        self.ui.parameterLayout.insertWidget(
            self.ui.parameterLayout.indexOf(self.ui.segmentTabWidget) + 1,
            self.highlightPulseCheckbox,
        )
        self.ui.parameterLayout.insertWidget(
            self.ui.parameterLayout.indexOf(self.ui.stepSlider),
            create_title("Stimulus dial"),
        )
        self.ui.parameterLayout.setAlignment(
            self.ui.stepSlider, Qt.AlignmentFlag.AlignLeft
        )
        self.ui.plotLayout.addWidget(create_title("Stimulus plot"))
        self.ui.plotLayout.addWidget(frame)
        self.plotWidget = plot

        self.ui.nSpinBox.valueChanged.connect(self.pulseChanged)
        self.ui.stepSlider.valueChanged.connect(self.stepChanged)
        self.ui.limitSpinBox.valueChanged.connect(self.pulseChanged)
        self.ui.durSpinBox.valueChanged.connect(self.pulseChanged)
        self.highlightPulseCheckbox.toggled.connect(self.pulseHighlightChanged.emit)

        spin_value_helper(
            self.ui.durSpinBox,
            default_val=DEFAULT_DUR_S,
            min_val=0.0001,
            max_val=1,
            step=SEGMENT_VIEW_STEP_S,
        )

        spin_value_helper(
            self.ui.limitSpinBox,
            default_val=DEFAULT_LIMIT_V,
            min_val=0.0,
            max_val=SEGMENT_VIEW_MAX_V,
            step=SEGMENT_VIEW_STEP_V,
        )

        self.pulseHighlightChanged.emit(self.highlightPulseCheckbox.isChecked())
        self.pulseChanged.emit()

    def setup_tabs(self):
        self.ui.segmentTabWidget.setTabsClosable(True)
        self.ui.segmentTabWidget.tabCloseRequested.connect(self.handle_close_tab)
        self.ui.segmentTabWidget.setMovable(True)
        self.ui.segmentTabWidget.tabBar().setUsesScrollButtons(True)
        self.ui.segmentTabWidget.tabBar().tabMoved.connect(self.handle_move_tab)
        self.ui.segmentTabWidget.currentChanged.connect(self.renumber_tabs)

        # Add base segment tab.
        self.add_segment_tab()

        new_segment_button = QPushButton("+")
        new_segment_button.setFixedWidth(25)
        new_segment_button.clicked.connect(self.add_segment_tab)
        self.ui.segmentTabWidget.setCornerWidget(
            new_segment_button, Qt.Corner.TopRightCorner
        )
        new_segment_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.ui.segmentTabWidget.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )

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

        if self.ui.stepSlider.value() > max_idx:
            self.ui.stepSlider.setValue(max_idx)

        # Emit stepChanged to update the plot.
        self.stepChanged.emit()

    def clear_plot(self):
        self.plotWidget.clear()

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

    def draw_pulse_bounds(self, lt, rt, tp, bt):
        guide_color = "b"

        # Mark the start of the pulse more clearly.
        self.plotWidget.addItem(
            create_guide_line(lt, 90, guide_color, style=Qt.PenStyle.DashLine)
        )
        self.plotWidget.addItem(create_guide_line(rt, 90, guide_color))
        self.plotWidget.addItem(create_guide_line(tp, 0, guide_color))
        self.plotWidget.addItem(create_guide_line(bt, 0, guide_color))

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
        self.pulseChanged.emit()
