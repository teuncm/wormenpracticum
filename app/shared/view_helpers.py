import pyqtgraph as pg
from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QTabBar,
    QVBoxLayout,
)

from app.shared.constants import (
    DOUBLE_SPIN_NUM_DECIMALS,
    LEFT_LAYOUT_STRETCH,
    PLOT_GRID_ALPHA_DEFAULT,
    RIGHT_LAYOUT_STRETCH,
    TITLE_LABEL_POINT_SIZE_INCREASE,
    VIEW_MARGIN_DEFAULT,
    VIEW_SPACING_DEFAULT,
)


def set_global_plot_config() -> None:
    """Configure the plot style globally."""
    pg.setConfigOptions(background="w", foreground="k", antialias=True)

    # Silently attempt to enable OpenGL for faster rendering.
    try:
        pg.setConfigOptions(useOpenGL=True)
        print("OpenGL enabled for rendering")
    except Exception:
        pg.setConfigOptions(useOpenGL=False)
        print("Falling back to CPU rendering")


def create_plot_widget(
    title=None,
    x_label=None,
    x_units=None,
    y_label=None,
    y_units=None,
    frame: QFrame | None = None,
) -> tuple[QFrame, pg.PlotWidget]:
    """Create a plot widget in a frame."""
    if frame is None:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)

    plot = pg.PlotWidget()
    plot.showGrid(x=True, y=True, alpha=PLOT_GRID_ALPHA_DEFAULT)
    plot.setMouseEnabled(x=False, y=False)
    plot.setClipToView(True)
    plot.setDownsampling(auto=False)
    plot.hideButtons()

    if title:
        plot.setTitle(title)
    if x_label:
        plot.setLabel("bottom", x_label, units=x_units)
    if y_label:
        plot.setLabel("left", y_label, units=y_units)

    layout.addWidget(plot)

    return frame, plot


def create_guide_line(
    position, angle, color="b", width=1, style=Qt.PenStyle.DotLine, alpha=255, zValue=0
) -> pg.InfiniteLine:

    c = pg.mkColor(color)
    c.setAlpha(alpha)

    guide_line = pg.InfiniteLine(
        pos=position,
        angle=angle,
        pen=pg.mkPen(
            color=c,
            width=width,
            style=style,
        ),
    )

    guide_line.setZValue(zValue)

    return guide_line


def double_spin_helper(
    spinbox: QDoubleSpinBox,
    default_val: float,
    min_val: float,
    max_val: float,
    step: float,
    decimals: int = DOUBLE_SPIN_NUM_DECIMALS,
):
    spinbox.setDecimals(decimals)
    spinbox.setRange(min_val, max_val)
    spinbox.setSingleStep(step)
    spinbox.setValue(default_val)


def spin_helper(
    spinbox: QSpinBox,
    default_val: int,
    min_val: int,
    max_val: int,
    step: int,
):
    spinbox.setRange(min_val, max_val)
    spinbox.setSingleStep(step)
    spinbox.setValue(default_val)


def style_label(label: QLabel, bold=False, point_size_increase=0) -> QLabel:
    label.setProperty("title_point_size_increase", point_size_increase)
    label.setProperty("title_bold", bold)
    apply_title_label_font(label)

    return label


def setup_ui_custom(parent_widget) -> None:
    """Apply custom UI setup for a widget. This is called in the __init__ of each view after setupUi."""
    style_title_labels(parent_widget)
    adjust_layout_flow(parent_widget)


def style_title_labels(parent_widget) -> None:
    """Automatically style all QLabel widgets with "title" in their object name as section titles."""
    for widget in parent_widget.findChildren(QLabel):
        if "title" in widget.objectName():
            style_label(
                widget,
                point_size_increase=TITLE_LABEL_POINT_SIZE_INCREASE,
                bold=False,
            )


def adjust_layout_flow(parent_widget) -> None:
    """Set stretch factors for the main layout to control how space is allocated.
    This is constant through the whole application to maintain consistency."""
    flow_layout = parent_widget.layout()

    if flow_layout is None:
        flow_layout = parent_widget.findChild(QHBoxLayout, "flowLayout")

    if flow_layout is not None:
        flow_layout.setStretch(0, LEFT_LAYOUT_STRETCH)
        flow_layout.setStretch(1, RIGHT_LAYOUT_STRETCH)

        spacer(
            flow_layout,
            margin_left=8,
            margin_top=8,
            margin_right=8,
            margin_bottom=8,
            spacing=12,
        )


def spacer(
    layout,
    margin=None,
    margin_left=VIEW_MARGIN_DEFAULT,
    margin_top=VIEW_MARGIN_DEFAULT,
    margin_right=VIEW_MARGIN_DEFAULT,
    margin_bottom=VIEW_MARGIN_DEFAULT,
    spacing=VIEW_SPACING_DEFAULT,
) -> QBoxLayout:
    """Set margins and spacing for a layout."""
    if margin is not None:
        margin_left = margin_top = margin_right = margin_bottom = margin

    layout.setContentsMargins(margin_left, margin_top, margin_right, margin_bottom)
    layout.setSpacing(spacing)

    return layout


def info_box(
    message="This is an info message.",
    title="Info",
) -> QMessageBox:
    """Create an information message box and return it."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    return msg_box


def set_font_size(point_size: int):
    app = QApplication.instance()

    if not isinstance(app, QApplication):
        return

    font = app.font()
    font.setPointSize(point_size)
    app.setFont(font)
    refresh_widget_fonts(app)


def refresh_widget_fonts(app: QApplication) -> None:
    """Refresh widgets that use explicit fonts or custom painting."""
    for widget in app.allWidgets():
        if (
            isinstance(widget, QLabel)
            and widget.property("title_point_size_increase") is not None
        ):
            apply_title_label_font(widget)

        if isinstance(widget, QTabBar):
            widget.setFont(app.font())
            widget.updateGeometry()
            widget.update()


def apply_title_label_font(label: QLabel) -> None:
    app = QApplication.instance()
    base_font = app.font() if isinstance(app, QApplication) else label.font()
    font = QFont(base_font)
    point_size_increase = int(label.property("title_point_size_increase") or 0)
    font.setPointSize(base_font.pointSize() + point_size_increase)
    font.setBold(bool(label.property("title_bold")))
    label.setFont(font)


class Blocker:
    """Context manager to block signals for multiple widgets.
    Useful when updating view components from the model.
    Usage:
        with Blocker(widget1, widget2, ...):
            # Signals from these widgets are blocked in this block
            ...
    """

    def __init__(self, *widgets):
        self._blocker = [QSignalBlocker(widget) for widget in widgets]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        del self._blocker
