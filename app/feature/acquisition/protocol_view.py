import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.acquisition.protocol_mapping import encode_stim_channel_pair
from app.feature.filter.filter_config import FilterConfig
from app.feature.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from app.shared.constants import (
    PLOT_PIN_SELECTED_PEN_WIDTH,
    PLOT_PIN_UNSELECTED_PEN_WIDTH,
)
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.protocol_window import Ui_ProtocolWindow


class PinStateButton(QPushButton):
    stateChanged = Signal(int)

    DEFAULT_STATE = 0
    GREEN_STATE = 1
    RED_STATE = 2
    BLUE_STATE = 3
    NUM_STATES = 4

    _STATE_STYLES = {
        DEFAULT_STATE: "",
        GREEN_STATE: "background-color: #2f9e44; color: white;",
        RED_STATE: "background-color: #c92a2a; color: white;",
        BLUE_STATE: "background-color: #1971c2; color: white;",
    }

    def __init__(self, text: str):
        super().__init__(text)
        self._pin_state = self.DEFAULT_STATE
        self.setCheckable(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._refresh_state_style()

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

    def set_pin_state(self, state: int):
        state %= self.NUM_STATES
        if state == self._pin_state:
            return

        self._pin_state = state
        self._refresh_state_style()
        self.stateChanged.emit(self._pin_state)

    def _refresh_state_style(self):
        self.setStyleSheet(
            f"min-width: 0px; padding: 0px; {self._STATE_STYLES[self._pin_state]}"
        )


class ProtocolView(QWidget):
    run_requested = Signal()
    protocolChanged = Signal()
    filterChanged = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.set_nidaq_status(NI_DAQ_UNAVAILABLE_STATUS)
        self._positive_channel = 0
        self._negative_channel = 1

        self.ui.pushButton.clicked.connect(self.request_run)
        self.ui.sampleRateDividerSpinBox.valueChanged.connect(self.protocolChanged)
        self.ui.lowPassHzDoubleSpinBox.setRange(0.0, 100000.0)
        self.ui.lowPassHzDoubleSpinBox.setDecimals(2)
        self.ui.lowPassHzDoubleSpinBox.valueChanged.connect(self.filterChanged)
        self.ui.suppress50HzCheckBox.toggled.connect(self.filterChanged)
        self.ui.removeDCOffsetCheckBox.toggled.connect(self.filterChanged)
        self.ui.pushButton_2.clicked.connect(self.filterChanged)

        self.setup_widgets()
        self.plot_pins()

    def setup_widgets(self):
        """Set up the main plot and controls."""
        frame, plot = create_plot_widget()

        self.ui.rightLayout.addWidget(frame)
        self.plotWidget = plot

        # Create a grid of 16 checkable buttons under the "Pins" label
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
            self.pinButtons.append(btn)

        # Add Select All / Deselect All buttons below the pin grid
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.setObjectName("selectAllPinsButton")
        deselect_all_btn.setObjectName("deselectAllPinsButton")

        def select_all():
            with Blocker(*self.pinButtons):
                for b in self.pinButtons:
                    b.setChecked(True)
            self.plot_pins()
            self.protocolChanged.emit()

        def deselect_all():
            with Blocker(*self.pinButtons):
                for b in self.pinButtons:
                    b.setChecked(False)
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
        try:
            title_index = self.ui.leftLayout.indexOf(self.ui.title_controls)
        except Exception:
            title_index = -1

        if title_index == -1:
            self.ui.leftLayout.addWidget(pins_container)
        else:
            self.ui.leftLayout.insertWidget(title_index + 1, pins_container)

        # frame, plot = create_plot_widget(frame=self.ui.pinFrame)

        # self.ui.rightLayout.addWidget(frame)
        # self.plotWidget = plot

        # if plot.plotItem is not None:
        #     left_axis = plot.plotItem.getAxis("left")
        #     left_axis.setVisible(False)

    def update_from_config(self, protocol_config: ProtocolConfig):
        """Update protocol controls from a config object."""
        with Blocker(
            self.ui.sampleRateDividerSpinBox,
            *self.pinButtons,
        ):
            self._positive_channel = protocol_config.positive_channel
            self._negative_channel = protocol_config.negative_channel
            self.ui.sampleRateDividerSpinBox.setValue(
                protocol_config.sample_rate_divider
            )
            selected_pins = set(protocol_config.selected_pins)
            for index, button in enumerate(self.pinButtons, start=1):
                button.setChecked(index in selected_pins)

    def to_config(self) -> ProtocolConfig:
        """Read the protocol controls into a config object."""
        return ProtocolConfig(
            positive_channel=self._positive_channel,
            negative_channel=self._negative_channel,
            selected_pins=[
                index
                for index, button in enumerate(self.pinButtons, start=1)
                if button.isChecked()
            ],
            sample_rate_divider=self.ui.sampleRateDividerSpinBox.value(),
        )

    def update_filter_from_config(self, filter_config: FilterConfig):
        """Update acquisition filter controls from a config object."""
        with Blocker(
            self.ui.lowPassHzDoubleSpinBox,
            self.ui.suppress50HzCheckBox,
            self.ui.removeDCOffsetCheckBox,
        ):
            self.ui.lowPassHzDoubleSpinBox.setValue(filter_config.low_pass_cutoff_hz)
            self.ui.suppress50HzCheckBox.setChecked(filter_config.suppress_50hz)
            self.ui.removeDCOffsetCheckBox.setChecked(filter_config.remove_dc_offset)

    def to_filter_config(self) -> FilterConfig:
        """Read the acquisition filter controls into a config object."""
        return FilterConfig(
            low_pass_cutoff_hz=self.ui.lowPassHzDoubleSpinBox.value(),
            suppress_50hz=self.ui.suppress50HzCheckBox.isChecked(),
            remove_dc_offset=self.ui.removeDCOffsetCheckBox.isChecked(),
        )

    def plot_pins(self):
        """Plot 16 vertical pins for visual reference of the NI-DAQ digital output channels."""
        plot_widget = getattr(self, "plotWidget", None)
        if plot_widget is None:
            return

        plot_widget.clear()

        measured = [i + 1 for i, b in enumerate(self.pinButtons) if b.isChecked()]

        for channel in range(1, 17):
            # first, draw the pin
            base_pen = pg.mkPen("gray", width=PLOT_PIN_UNSELECTED_PEN_WIDTH)
            plot_widget.plot([channel, channel], [0, 1], pen=base_pen)

            # highlight measured pins
            if channel in measured:
                c = pg.mkColor("g")
                c.setAlpha(110)
                highlight_pen = pg.mkPen(c, width=PLOT_PIN_SELECTED_PEN_WIDTH)
                plot_widget.plot([channel, channel], [0, 1], pen=highlight_pen)

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
