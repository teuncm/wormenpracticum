from functools import partial

import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTabWidget

from app.app_model import AppModel
from app.feature.filter.filter_controls import FilterControls
from app.feature.filter.filter_view import FilterView
from app.feature.filter.filters import filter_recording, recording_sample_rate
from app.shared.constants import DEFAULT_FILTER_CONFIG
from app.shared.deferred_tab_draw import DeferredTabDraw
from app.shared.recording_metadata import recording_pin_channels


class FilterController:
    """Controller for managing data filters in the app."""

    def __init__(
        self, app_model: AppModel, view: FilterView, *, tabs: QTabWidget | None = None
    ):
        self.app_model = app_model
        self.view = view
        self._recording = None
        self._metadata = None
        self._sample_rate = None
        self._last_low_pass_cutoff = (
            app_model.filter_config.low_pass_cutoff_hz
            or DEFAULT_FILTER_CONFIG.low_pass_cutoff_hz
        )
        self._auto_update = True
        self._editors: list[FilterControls] = []
        self._pending_editor: FilterControls | None = None

        # Coalesce slider moves without waiting for the user to release the handle.
        self._live_update = QTimer(view)
        self._live_update.setSingleShot(True)
        self._live_update.setInterval(30)
        self._live_update.timeout.connect(self._apply_pending_filters)
        if tabs is not None:
            # Commit the outgoing tab's last edit before the new tab draws or edits.
            tabs.currentChanged.connect(self._apply_pending_filters)

        page = view.parentWidget() if tabs is not None else None
        self._preview_draw = DeferredTabDraw(self.update_preview, page, tabs)
        self.view.channel_changed.connect(self._preview_draw.request)
        self.app_model.filter_config_changed.connect(self.update_ui_from_model)
        self.app_model.experiment_data_changed.connect(self.update_recording)

        self.register_controls(self.view.filter_controls)
        self.update_recording()

    def register_controls(self, controls: FilterControls) -> None:
        """Connect another editor to the same model and live filter pass."""
        self._editors.append(controls)
        controls.set_config(
            self.app_model.filter_config, inactive_cutoff=self._last_low_pass_cutoff
        )
        controls.set_auto_update(self._auto_update)
        self._set_recording_state(controls)
        controls.settings_changed.connect(
            partial(self.schedule_filter_update, controls)
        )
        controls.auto_update_changed.connect(self._set_auto_update)

    def _set_auto_update(self, enabled: bool) -> None:
        self._auto_update = enabled
        for controls in self._editors:
            controls.set_auto_update(enabled)

    def _set_recording_state(self, controls: FilterControls) -> None:
        controls.set_recording_available(
            self.view.channel_selector.count() > 0, self._sample_rate
        )

    def update_recording(self) -> None:
        """Refresh channel choices on load and redraw from the filtered copy."""
        raw = self.app_model.raw_data_df
        metadata = self.app_model.experiment_metadata

        # Filtering emits the same signal as loading data. Keep the selector intact on live updates.
        if raw is not self._recording or metadata is not self._metadata:
            self.update_ui_from_model()
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
            for controls in self._editors:
                self._set_recording_state(controls)

        self._preview_draw.request()

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

    def schedule_filter_update(self, controls: FilterControls) -> None:
        if not self.view.channel_selector.count():
            return
        self._pending_editor = controls
        if not self._live_update.isActive():
            self._live_update.start()

    def _cancel_pending_update(self) -> None:
        self._live_update.stop()
        self._pending_editor = None

    def _apply_pending_filters(self) -> None:
        if self._pending_editor is not None:
            self.apply_filters(self._pending_editor)

    def apply_filters(self, controls: FilterControls) -> None:
        """Start from raw data every time and publish only a successful result."""
        self._cancel_pending_update()
        raw = self.app_model.raw_data_df
        if raw is None or raw.empty:
            return

        config = controls.to_config()
        try:
            filtered = filter_recording(
                raw,
                config,
                self._sample_rate
                if self._sample_rate is not None
                else self.app_model.experiment_metadata.get("sample_rate_hz"),
            )
        except (ValueError, TypeError) as error:
            controls.show_status(f"Could not apply filters. {error}")
            return

        if self.app_model.filter_config == config:
            self.update_ui_from_model()
        else:
            self.app_model.update_filter_config(config)
        self.app_model.update_filtered_data(filtered)
        for editor in self._editors:
            editor.show_status("")

    def update_ui_from_model(self):
        self._cancel_pending_update()
        config = self.app_model.filter_config
        if config.low_pass_cutoff_hz:
            self._last_low_pass_cutoff = config.low_pass_cutoff_hz
        for controls in self._editors:
            # Keep the last applied cutoff while storing Off as zero in saved protocols.
            if not config.low_pass_cutoff_hz or controls.to_config() != config:
                controls.set_config(config, inactive_cutoff=self._last_low_pass_cutoff)
