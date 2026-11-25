import numpy as np
from PySide6.QtCore import QTimer

from app.app_model import AppModel
from app.feature.filter.filter_view import FilterView
from app.feature.filter.filters import filter_recording, recording_sample_rate
from app.shared.recording_metadata import recording_pin_channels


class FilterController:
    """Controller for managing data filters in the app."""

    def __init__(self, app_model: AppModel, view: FilterView):
        self.app_model = app_model
        self.view = view
        self._recording = None
        self._metadata = None
        self._sample_rate = None

        # Coalesce slider moves without waiting for the user to release the handle.
        self._live_update = QTimer(view)
        self._live_update.setSingleShot(True)
        self._live_update.setInterval(30)
        self._live_update.timeout.connect(self.apply_filters)

        self.view.apply_requested.connect(self.apply_filters)
        self.view.settings_changed.connect(self.schedule_filter_update)
        self.view.channel_changed.connect(self.update_preview)
        self.app_model.filter_config_changed.connect(self.update_ui_from_model)
        self.app_model.experiment_data_changed.connect(self.update_recording)

        self.update_ui_from_model()
        self.update_recording()

    def update_recording(self) -> None:
        """Refresh channel choices on load and redraw from the filtered copy."""
        raw = self.app_model.raw_data_df
        metadata = self.app_model.experiment_metadata

        # Filtering emits the same signal as loading data. Keep the selector intact on live updates.
        if raw is not self._recording or metadata is not self._metadata:
            self._live_update.stop()
            self._recording, self._metadata = raw, metadata
            self._sample_rate = None
            channels = []
            if raw is not None and not raw.empty:
                mapping = recording_pin_channels(metadata)
                for column in raw:
                    if column != "t_(s)":
                        pin = mapping.get(column)
                        channels.append(
                            (column, f"Pin {pin}: {column}" if pin else column)
                        )

                try:
                    self._sample_rate = recording_sample_rate(
                        raw, metadata.get("sample_rate_hz")
                    )
                except (ValueError, TypeError):
                    # Time-independent filters can still run on these recordings.
                    pass

            self.view.set_channels(channels)
            self.view.set_sample_rate(self._sample_rate if channels else None)
            self.view.apply_button.setEnabled(bool(channels))
            self.view.status.setText(
                "Adjust the filters to update the signal live."
                if channels
                else "Record or load data with voltage channels."
            )

        self.update_preview()

    def update_preview(self) -> None:
        """Draw the selected channel from the same samples used in analysis."""
        data = self.app_model.filtered_data_df
        column = self.view.channel_selector.currentData()
        if data is None or column not in data:
            self.view.clear_preview()
            return

        try:
            samples = data[column].to_numpy(dtype=float)
            if "t_(s)" in data:
                x = data["t_(s)"].to_numpy(dtype=float)
            elif self._sample_rate is not None:
                x = np.arange(len(data)) / self._sample_rate
            else:
                x = np.arange(len(data))
        except (ValueError, TypeError):
            self.view.clear_preview()
            return

        has_time = "t_(s)" in data or self._sample_rate is not None
        self.view.show_preview(x, samples, has_time=has_time)

    def schedule_filter_update(self) -> None:
        if self.view.apply_button.isEnabled() and not self._live_update.isActive():
            self._live_update.start()

    def apply_filters(self) -> None:
        """Start from raw data every time and publish only a successful result."""
        self._live_update.stop()
        raw = self.app_model.raw_data_df
        if raw is None or raw.empty:
            return

        config = self.view.to_config()
        try:
            filtered = filter_recording(
                raw,
                config,
                self._sample_rate
                if self._sample_rate is not None
                else self.app_model.experiment_metadata.get("sample_rate_hz"),
            )
        except (ValueError, TypeError) as error:
            self.view.status.setText(f"Could not apply filters. {error}")
            return

        self.app_model.update_filter_config(config)
        self.app_model.update_filtered_data(filtered)
        self.view.status.setText("Analysis views updated.")

    def update_ui_from_model(self):
        self._live_update.stop()
        if self.view.to_config() != self.app_model.filter_config:
            self.view.set_config(self.app_model.filter_config)
