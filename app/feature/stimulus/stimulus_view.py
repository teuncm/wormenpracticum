import pyqtgraph as pg
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QDialog,
    QSizePolicy,
    QTabBar,
)

from app.shared.constants import (
    DEFAULT_DUR_S,
    DEFAULT_LIMIT_V,
    DOUBLE_SPIN_MAX_V,
    DOUBLE_SPIN_STEP_S,
    DOUBLE_SPIN_STEP_V,
    SEGMENT_VIEW_STIMULUS_HIGHLIGHT_DEFAULT,
)
from app.feature.stimulus.pulse_tab_view import PulseTabView
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


class StimulusView(QDialog):
    stimulusChanged = Signal()
    stepChanged = Signal()
    stimulusHighlightChanged = Signal(bool)

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
        self.ui.limitSpinBox.valueChanged.connect(self.stimulusChanged)
        self.ui.durSpinBox.valueChanged.connect(self.stimulusChanged)
        self.ui.highlight_selected_pulse_checkbox.toggled.connect(
            self.stimulusHighlightChanged.emit
        )

        self.stimulusHighlightChanged.emit(
            self.ui.highlight_selected_pulse_checkbox.isChecked()
        )

    def setup_widgets(self):
        self.ui.highlight_selected_pulse_checkbox.setChecked(
            SEGMENT_VIEW_STIMULUS_HIGHLIGHT_DEFAULT
        )

        frame, plot = create_plot_widget()
        self.ui.stepSlider.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.ui.rightLayout.addWidget(frame)
        self.plotWidget = plot

        double_spin_helper(
            self.ui.durSpinBox,
            default_val=DEFAULT_DUR_S,
            min_val=0.0001,
            max_val=1,
            step=DOUBLE_SPIN_STEP_S,
        )

        double_spin_helper(
            self.ui.limitSpinBox,
            default_val=DEFAULT_LIMIT_V,
            min_val=0.0,
            max_val=DOUBLE_SPIN_MAX_V,
            step=DOUBLE_SPIN_STEP_V,
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
        segment = PulseTabView()

        index = self.ui.segmentTabWidget.addTab(segment, "")
        self.ui.segmentTabWidget.setCurrentIndex(index)

        segment.segmentChanged.connect(self.stimulusChanged)
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

    def draw_segment_bounds(self, lt, rt, tp, bt, center=None):
        guide_color = "b"

        # Mark segment bounds more clearly.
        self.plotWidget.addItem(
            create_guide_line(lt, 90, guide_color, style=Qt.PenStyle.DashLine)
        )
        self.plotWidget.addItem(create_guide_line(rt, 90, guide_color))
        if center is not None:
            self.plotWidget.addItem(create_guide_line(center, 90, guide_color))
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
        self.stimulusChanged.emit()
