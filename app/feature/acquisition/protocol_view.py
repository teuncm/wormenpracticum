import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.shared.constants import (
    PLOT_PIN_SELECTED_PEN_WIDTH,
    PLOT_PIN_UNSELECTED_PEN_WIDTH,
)
from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from app.feature.acquisition.protocol_mapping import (
    encode_stim_channel_pair,
    get_logical_channel_labels,
)
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom
from app.ui.generated.protocol_window import Ui_ProtocolWindow


class ProtocolView(QWidget):
    run_requested = Signal()
    protocolChanged = Signal()

    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)

        setup_ui_custom(self)

        self.set_nidaq_status(NI_DAQ_UNAVAILABLE_STATUS)

        self.populate_channel_dropdowns()
        self.ui.pushButton.clicked.connect(self.request_run)
        self.ui.positiveChannelComboBox.currentIndexChanged.connect(self.plot_pins)
        self.ui.negativeChannelComboBox.currentIndexChanged.connect(self.plot_pins)
        self.ui.positiveChannelComboBox.currentIndexChanged.connect(
            self.protocolChanged
        )
        self.ui.negativeChannelComboBox.currentIndexChanged.connect(
            self.protocolChanged
        )
        self.ui.sampleRateDividerSpinBox.valueChanged.connect(self.protocolChanged)

        self.setup_widgets()
        self.plot_pins()

    def setup_widgets(self):
        """Set up the main plot and controls."""
        frame, plot = create_plot_widget()

        self.ui.rightLayout.addWidget(frame)
        self.plotWidget = plot

        if plot.plotItem is not None:
            left_axis = plot.plotItem.getAxis("left")
            left_axis.setVisible(False)

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
            btn = QPushButton(str(i + 1))
            btn.setCheckable(True)
            btn.setObjectName(f"pinButton{i + 1}")
            btn.setMinimumSize(0, button_h)
            btn.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet("min-width: 0px; padding: 0px;")
            pins_layout.addWidget(btn, i // 8, i % 8)
            btn.toggled.connect(self.plot_pins)
            btn.toggled.connect(self.protocolChanged)
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

        # Insert the pins container under the existing pins_label (before the placeholder label)
        try:
            placeholder_index = self.ui.leftLayout.indexOf(self.ui.label)
        except Exception:
            placeholder_index = -1

        if placeholder_index == -1:
            self.ui.leftLayout.addWidget(pins_container)
        else:
            self.ui.leftLayout.insertWidget(placeholder_index, pins_container)

    def update_from_config(self, protocol_config: ProtocolConfig):
        """Update protocol controls from a config object."""
        with Blocker(
            self.ui.positiveChannelComboBox,
            self.ui.negativeChannelComboBox,
            self.ui.sampleRateDividerSpinBox,
            *self.pinButtons,
        ):
            self.ui.positiveChannelComboBox.setCurrentIndex(
                protocol_config.positive_channel
            )
            self.ui.negativeChannelComboBox.setCurrentIndex(
                protocol_config.negative_channel
            )
            self.ui.sampleRateDividerSpinBox.setValue(
                protocol_config.sample_rate_divider
            )
            selected_pins = set(protocol_config.selected_pins)
            for index, button in enumerate(self.pinButtons, start=1):
                button.setChecked(index in selected_pins)

        self.plot_pins()

    def to_config(self) -> ProtocolConfig:
        """Read the protocol controls into a config object."""
        return ProtocolConfig(
            positive_channel=self.ui.positiveChannelComboBox.currentIndex(),
            negative_channel=self.ui.negativeChannelComboBox.currentIndex(),
            selected_pins=[
                index
                for index, button in enumerate(self.pinButtons, start=1)
                if button.isChecked()
            ],
            sample_rate_divider=self.ui.sampleRateDividerSpinBox.value(),
        )

    def plot_pins(self):
        """Plot 16 vertical pins for visual reference of the NI-DAQ digital output channels."""
        if not hasattr(self, "plotWidget"):
            return

        self.plotWidget.clear()

        positive_channel, negative_channel = self.get_selected_stim_channels()

        measured = [i + 1 for i, b in enumerate(self.pinButtons) if b.isChecked()]

        for channel in range(1, 17):
            # first, draw the pin
            base_pen = pg.mkPen("gray", width=PLOT_PIN_UNSELECTED_PEN_WIDTH)
            self.plotWidget.plot([channel, channel], [0, 1], pen=base_pen)

            # highlight measured pins
            if channel in measured:
                c = pg.mkColor("g")
                c.setAlpha(110)
                highlight_pen = pg.mkPen(c, width=PLOT_PIN_SELECTED_PEN_WIDTH)
                self.plotWidget.plot([channel, channel], [0, 1], pen=highlight_pen)

            # overlay translucent pens for positive/negative so both remain visible
            if channel == positive_channel:
                c = pg.mkColor("b")
                c.setAlpha(110)
                pos_pen = pg.mkPen(color=c, width=PLOT_PIN_SELECTED_PEN_WIDTH)
                self.plotWidget.plot([channel, channel], [0, 1], pen=pos_pen)

            if channel == negative_channel:
                c = pg.mkColor("r")
                c.setAlpha(110)
                neg_pen = pg.mkPen(color=c, width=PLOT_PIN_SELECTED_PEN_WIDTH)
                self.plotWidget.plot([channel, channel], [0, 1], pen=neg_pen)

    def request_run(self):
        self.run_requested.emit()

    def populate_channel_dropdowns(self):
        channel_labels = get_logical_channel_labels()

        self.ui.positiveChannelComboBox.clear()
        self.ui.negativeChannelComboBox.clear()

        for channel_number, channel_label in enumerate(channel_labels, start=1):
            self.ui.positiveChannelComboBox.addItem(channel_label, channel_number)
            self.ui.negativeChannelComboBox.addItem(channel_label, channel_number)

        # Match the MATLAB defaults: stim1 = 1, stim2 = 2.
        self.ui.positiveChannelComboBox.setCurrentIndex(0)
        if self.ui.negativeChannelComboBox.count() > 1:
            self.ui.negativeChannelComboBox.setCurrentIndex(1)

    def get_selected_stim_channels(self):
        positive_channel = self.ui.positiveChannelComboBox.currentData()
        negative_channel = self.ui.negativeChannelComboBox.currentData()

        if positive_channel is None or negative_channel is None:
            raise ValueError("Stim channel dropdowns are not populated")

        return int(positive_channel), int(negative_channel)

    def get_encoded_stim_port_values(self):
        positive_channel, negative_channel = self.get_selected_stim_channels()
        return encode_stim_channel_pair(positive_channel, negative_channel)

    def set_nidaq_status(self, status: str):
        """Set the nidaq status label in the UI."""
        self.ui.nidaqStatusLabel.setText(f"Status: {status}")
