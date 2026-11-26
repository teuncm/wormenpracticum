import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.feature.filter.filter_controls import FilterControls
from app.shared.view_helpers import Blocker, create_plot_widget, setup_ui_custom


class FilterView(QWidget):
    """Edit filters beside a live preview of the filtered recording."""

    channel_changed = Signal()

    def __init__(self):
        super().__init__()

        self.filter_controls = FilterControls()
        self.channel_selector = QComboBox()
        self.channel_selector.setAccessibleName("Preview channel")

        settings_title = QLabel("Filter settings")
        settings_title.setObjectName("title_filter_settings")
        settings = QFormLayout()
        settings.addRow("Preview channel", self.channel_selector)

        controls = QVBoxLayout()
        controls.addWidget(settings_title)
        controls.addLayout(settings)
        controls.addWidget(self.filter_controls)
        controls.addStretch()

        preview_title = QLabel("Filtered signal")
        preview_title.setObjectName("title_filter_preview")
        frame, self.plot = create_plot_widget(
            x_label="Time", x_units="s", y_label="Voltage", y_units="V"
        )
        self.preview_curve = self.plot.plot(pen="#2166ac", connect="finite")
        self.plot.setDownsampling(auto=True, mode="peak")

        visuals = QVBoxLayout()
        visuals.addWidget(preview_title)
        visuals.addWidget(frame, 1)

        layout = QHBoxLayout(self)
        layout.addLayout(controls)
        layout.addLayout(visuals)
        setup_ui_custom(self)

        self.channel_selector.currentIndexChanged.connect(
            lambda _index: self.channel_changed.emit()
        )

    def set_channels(self, channels: list[tuple[str, str]]) -> None:
        selected = self.channel_selector.currentData()

        with Blocker(self.channel_selector):
            self.channel_selector.clear()
            for column, label in channels:
                self.channel_selector.addItem(label, column)
            previous_index = self.channel_selector.findData(selected)
            self.channel_selector.setCurrentIndex(max(0, previous_index))

        self.channel_selector.setEnabled(bool(channels))

    def show_preview(
        self, x: np.ndarray, samples: np.ndarray, *, has_time: bool
    ) -> None:
        """Render the selected trace and fit its axes to the filtered samples."""
        self.plot.setLabel(
            "bottom", "Time" if has_time else "Sample", units="s" if has_time else ""
        )
        self.preview_curve.setData(x, samples)
        self.plot.autoRange()

    def clear_preview(self) -> None:
        self.preview_curve.clear()
