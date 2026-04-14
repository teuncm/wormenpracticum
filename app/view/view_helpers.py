import pyqtgraph as pg
from app.constants import (
    PLOT_GRID_ALPHA_DEFAULT,
    SEGMENT_VIEW_NUM_DECIMALS,
    VIEW_MARGIN_DEFAULT,
    VIEW_SPACING_DEFAULT,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QDoubleSpinBox, QFrame, QLabel, QVBoxLayout


def set_global_plot_config() -> None:
    """Configure the plot style globally."""
    pg.setConfigOptions(background="w", foreground="k", antialias=True)


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
    plot.setDownsampling(auto=True)
    plot.hideButtons()

    if title:
        plot.setTitle(title)
    if x_label:
        plot.setLabel("bottom", x_label, units=x_units)
    if y_label:
        plot.setLabel("left", y_label, units=y_units)

    layout.addWidget(plot)

    return frame, plot


def spin_value_helper(
    spinbox: QDoubleSpinBox,
    default_val: float,
    min_val: float,
    max_val: float,
    step: float,
    decimals: int = SEGMENT_VIEW_NUM_DECIMALS,
):
    spinbox.setRange(min_val, max_val)
    spinbox.setSingleStep(step)
    spinbox.setDecimals(decimals)
    spinbox.setValue(default_val)


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
