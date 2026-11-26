from typing import ClassVar

import pyqtgraph as pg
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsPathItem,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.feature.acquisition.protocol_config import SAMPLE_RATE_DIVIDERS, ProtocolConfig
from app.feature.acquisition.protocol_mapping import encode_stim_channel_pair
from app.feature.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from app.shared.constants import (
    PLOT_PIN_SELECTED_PEN_WIDTH,
    PLOT_PIN_UNSELECTED_PEN_WIDTH,
)
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.protocol_window import Ui_ProtocolWindow


class PinStateButton(QPushButton):
    stateChanged = Signal(int)
    hoverChanged = Signal()

    DEFAULT_STATE = 0
    GREEN_STATE = 1
    RED_STATE = 2
    BLUE_STATE = 3
    NUM_STATES = 4

    STATE_APPEARANCE: ClassVar[dict[int, tuple[str, str, str]]] = {
        RED_STATE: ("Stim +", "#c92a2a", "+"),
        BLUE_STATE: ("Stim -", "#1971c2", "-"),
        GREEN_STATE: ("Record (R)", "#2f9e44", "R"),
        DEFAULT_STATE: ("Off (0)", "gray", "0"),
    }

    def __init__(self, text: str):
        super().__init__(text)
        self._pin_state = self.DEFAULT_STATE
        self.setCheckable(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._refresh_state_style()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.hoverChanged.emit()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hoverChanged.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_pin_state(self._pin_state + 1)
            event.accept()
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.set_pin_state(self._pin_state - 1)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def setChecked(self, checked: bool):
        self.set_pin_state(self.GREEN_STATE if checked else self.DEFAULT_STATE)

    def isChecked(self) -> bool:
        return self._pin_state != self.DEFAULT_STATE

    @property
    def pin_state(self) -> int:
        """Return the current pin assignment."""
        return self._pin_state

    def set_pin_state(self, state: int):
        state %= self.NUM_STATES
        if state == self._pin_state:
            return

        self._pin_state = state
        self._refresh_state_style()
        self.stateChanged.emit(self._pin_state)

    def pin_color(self) -> str:
        """Return the shared color for this pin button and its plot bar."""
        return self.STATE_APPEARANCE[self._pin_state][1]

    def role_marker(self) -> str:
        """Return the short role label that fits under the pin number."""
        return self.STATE_APPEARANCE[self._pin_state][2]

    def _refresh_state_style(self):
        style = "min-width: 0px; padding: 0px;"
        if self.isChecked():
            style += f" background-color: {self.pin_color()}; color: white;"
        self.setStyleSheet(style)


class ProtocolView(QWidget):
    run_requested = Signal()
    protocolChanged = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.set_nidaq_status(NI_DAQ_UNAVAILABLE_STATUS)
        self._positive_channel = 0
        self._negative_channel = 1
        self._max_sample_rate_hz = 0.0

        for divider in SAMPLE_RATE_DIVIDERS:
            self.ui.sampleRateDividerComboBox.addItem(str(divider), divider)

        self.ui.pushButton.clicked.connect(self.request_run)
        self.ui.sampleRateDividerComboBox.currentIndexChanged.connect(
            self._on_sample_rate_divider_changed
        )
        self.setup_widgets()
        self.plot_pins()

    def setup_widgets(self):
        """Set up the main plot and controls."""
        frame, plot = create_plot_widget(x_label="Pin number")
        plot.hideAxis("left")
        plot.showGrid(x=False, y=False)
        pin_numbers = range(1, 17)
        pin_axis = plot.getAxis("bottom")
        pin_axis.setStyle(tickLength=0)

        self.ui.rightLayout.addWidget(frame)
        self.ui.rightLayout.addLayout(self._create_pin_legend())
        self.plotWidget = plot
        # Pin positions never change; selection should only change their styling.
        plot.setRange(xRange=(0.5, 16.5), yRange=(0, 1.05), padding=0)
        self._pin_bars = [plot.plot([pin, pin], [0, 1]) for pin in pin_numbers]

        self._pin_outline = QGraphicsPathItem()
        self._pin_outline.setPen(pg.mkPen(pin_axis.pen().color(), width=2))
        self._pin_outline.hide()
        plot.getViewBox().addItem(self._pin_outline, ignoreBounds=True)

        # Create a grid of 16 buttons that cycle through the pin colors.
        pins_container = QWidget()
        pins_container_layout = QVBoxLayout(pins_container)
        pins_container_layout.setContentsMargins(0, 0, 0, 0)
        pins_container_layout.setSpacing(4)

        pins_layout = QGridLayout()
        pins_layout.setContentsMargins(0, 0, 0, 0)
        pins_layout.setSpacing(4)
        pins_container_layout.addLayout(pins_layout)

        # Keep columns even while letting pin buttons follow the available width.
        button_h = 26
        for col in range(8):
            pins_layout.setColumnMinimumWidth(col, 0)
            pins_layout.setColumnStretch(col, 1)

        # Keep the container from expanding vertically too much
        pins_container.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.pinButtons = []
        for i in range(16):
            btn = PinStateButton(str(i + 1))
            btn.setObjectName(f"pinButton{i + 1}")
            btn.setMinimumSize(0, button_h)
            btn.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            pins_layout.addWidget(btn, i // 8, i % 8)
            btn.stateChanged.connect(lambda _state: self.plot_pins())
            btn.stateChanged.connect(lambda _state: self.protocolChanged.emit())
            btn.hoverChanged.connect(self.plot_pins)
            self.pinButtons.append(btn)

        # Add Select All / Deselect All buttons below the pin grid
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.setObjectName("selectAllPinsButton")
        deselect_all_btn.setObjectName("deselectAllPinsButton")

        def select_all():
            """Select unused pins while preserving the current pin assignments."""
            with Blocker(*self.pinButtons):
                for button in self.pinButtons:
                    if not button.isChecked():
                        button.setChecked(True)
            self.plot_pins()
            self.protocolChanged.emit()

        def deselect_all():
            """Turn off green pins while preserving input/output assignments."""
            with Blocker(*self.pinButtons):
                for button in self.pinButtons:
                    if button.pin_state == PinStateButton.GREEN_STATE:
                        button.setChecked(False)
            self.plot_pins()
            self.protocolChanged.emit()

        select_all_btn.clicked.connect(select_all)
        deselect_all_btn.clicked.connect(deselect_all)

        # Keep the action buttons out of the pin grid so they do not widen columns.
        pin_actions_layout = QHBoxLayout()
        pin_actions_layout.setContentsMargins(0, 0, 0, 0)
        pin_actions_layout.setSpacing(4)
        pin_actions_layout.addStretch()
        pin_actions_layout.addWidget(select_all_btn)
        pin_actions_layout.addWidget(deselect_all_btn)
        pin_actions_layout.addStretch()
        pins_container_layout.addLayout(pin_actions_layout)

        # Keep the pin grid at the top of the left controls column.
        title_index = self.ui.leftLayout.indexOf(self.ui.title_controls)

        if title_index == -1:
            self.ui.leftLayout.addWidget(pins_container)
        else:
            self.ui.leftLayout.insertWidget(title_index + 1, pins_container)

    def _create_pin_legend(self) -> QHBoxLayout:
        """Pair each pin role with the same color used in the plot."""
        legend = QHBoxLayout()
        legend.setSpacing(12)
        legend.addStretch()
        for role, color, _marker in PinStateButton.STATE_APPEARANCE.values():
            entry = QHBoxLayout()
            entry.setSpacing(5)

            swatch = QFrame()
            swatch.setFixedSize(12, 4)
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            entry.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignVCenter)
            entry.addWidget(QLabel(role))
            legend.addLayout(entry)
        legend.addStretch()
        return legend

    def update_from_config(self, protocol_config: ProtocolConfig):
        """Update protocol controls from a config object."""
        with Blocker(
            self.ui.sampleRateDividerComboBox,
            *self.pinButtons,
        ):
            self._positive_channel = protocol_config.positive_channel
            self._negative_channel = protocol_config.negative_channel
            combo = self.ui.sampleRateDividerComboBox
            combo.setCurrentIndex(combo.findData(protocol_config.sample_rate_divider))
            selected_pins = set(protocol_config.selected_pins)
            for index, button in enumerate(self.pinButtons, start=1):
                # Stimulation channels are zero-based; pin labels are one-based.
                if index == protocol_config.positive_channel + 1:
                    button.set_pin_state(PinStateButton.RED_STATE)
                elif index == protocol_config.negative_channel + 1:
                    button.set_pin_state(PinStateButton.BLUE_STATE)
                else:
                    button.setChecked(index in selected_pins)
        self._update_sample_rate_labels()
        self.plot_pins()

    def to_config(self) -> ProtocolConfig:
        """Read the protocol controls into a config object."""
        return ProtocolConfig(
            positive_channel=self._positive_channel,
            negative_channel=self._negative_channel,
            selected_pins=[
                index
                for index, button in enumerate(self.pinButtons, start=1)
                if button.pin_state == PinStateButton.GREEN_STATE
            ],
            sample_rate_divider=self.ui.sampleRateDividerComboBox.currentData(),
        )

    def set_max_sample_rate(self, sample_rate_hz: float):
        """Update the maximum rate and the displayed rate after division."""
        self._max_sample_rate_hz = sample_rate_hz
        self._update_sample_rate_labels()

    def _update_sample_rate_labels(self):
        """Display both sample rates in Hz using the selected divider."""
        divider = self.ui.sampleRateDividerComboBox.currentData()
        self.ui.maxSampleRateLabel.setText(f"{self._max_sample_rate_hz:g} Hz")
        self.ui.actualSampleRateLabel.setText(
            f"{self._max_sample_rate_hz / divider:g} Hz"
        )

    def _on_sample_rate_divider_changed(self, *_):
        """Refresh the displayed rate and publish the protocol change."""
        self._update_sample_rate_labels()
        self.protocolChanged.emit()

    def plot_pins(self):
        """Match each bar to its button and emphasize the hovered pin."""
        # Keep each role under its pin number without crowding neighboring pins.
        labels = [
            (pin, f"{pin}\n{button.role_marker()}")
            for pin, button in enumerate(self.pinButtons, start=1)
        ]
        self.plotWidget.getAxis("bottom").setTicks([labels])
        self._pin_outline.hide()
        for button, bar in zip(self.pinButtons, self._pin_bars):
            hovered = button.underMouse()
            bar.setVisible(not hovered)

            width = (
                PLOT_PIN_SELECTED_PEN_WIDTH
                if button.isChecked()
                else PLOT_PIN_UNSELECTED_PEN_WIDTH
            )
            pen = pg.mkPen(button.pin_color(), width=width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            bar.setPen(pen)

            if hovered:
                pin = bar.xData[0]
                bottom, top = bar.yData

                # Use a fraction of the spacing between pins so the outline scales with the plot.
                path = QPainterPath()
                rect = QRectF(pin - 0.1, bottom, 0.2, top - bottom)
                path.addRoundedRect(rect, 100, 2.5, Qt.SizeMode.RelativeSize)
                self._pin_outline.setPath(path)
                fill = button.pin_color() if button.isChecked() else None
                self._pin_outline.setBrush(pg.mkBrush(fill))
                self._pin_outline.show()

    def request_run(self):
        self.run_requested.emit()

    def get_selected_stim_channels(self):
        return self._positive_channel + 1, self._negative_channel + 1

    def get_encoded_stim_port_values(self):
        positive_channel, negative_channel = self.get_selected_stim_channels()
        return encode_stim_channel_pair(positive_channel, negative_channel)

    def set_nidaq_status(self, status: str):
        """Set the nidaq status label in the UI."""
        self.ui.nidaqStatusLabel.setText(f"Status: {status}")
