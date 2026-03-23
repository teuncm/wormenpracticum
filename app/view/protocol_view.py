from app.model.protocol_mapping import (
    encode_stim_channel_pair,
    get_logical_channel_labels,
)
from app.window.ui_protocol_window import Ui_ProtocolWindow
from PySide6.QtWidgets import (
    QDialog,
)


class ProtocolView(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ProtocolWindow()
        self.ui.setupUi(self)
        self.populate_channel_dropdowns()

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
