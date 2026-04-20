import pyqtgraph as pg
from app.constants import (
    DOUBLE_SPIN_NUM_DECIMALS,
    PLOT_GRID_ALPHA_DEFAULT,
    VIEW_MARGIN_DEFAULT,
    VIEW_SPACING_DEFAULT,
)
from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
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
    title=None, x_label=None, x_units=None, y_label=None, y_units=None
) -> tuple[QFrame, pg.PlotWidget]:
    """Create a plot widget in a frame."""
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


def create_title(title_text, bold=True) -> QLabel:
    """Create a section title."""
    title = QLabel(title_text)
    font = title.font()
    font.setBold(bold)
    # font.setPointSize(font.pointSize() + 1)
    title.setFont(font)

    return title


def create_attribution_row(name_text: str, description_text: str) -> QWidget:
    """Create a single attribution row with a bold name and neutral description."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    layout.addWidget(create_title(name_text))

    description = QLabel(description_text)
    description.setWordWrap(True)
    layout.addWidget(description, 1)

    return row


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


def info_box(title="Info", message="This is an info message."):
    """Show an information message box."""
    QMessageBox.information(None, title, message)


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
