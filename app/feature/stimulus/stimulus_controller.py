from PySide6.QtCore import QPointF

from app.app_model import AppModel
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.pulse_tab_view import PulseTabView
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_view import StimulusView
from app.shared.constants import (
    DEFAULT_LIMIT_V,
    DOUBLE_SPIN_PARSE_ROUND_DECIMALS,
    TARGET_N_SAMPLES_PULSE_PLOT,
)
from app.shared.view_helpers import Blocker


class StimulusController:
    def __init__(self, app_model: AppModel, stimulus_view: StimulusView):
        self.app_model = app_model
        self.stimulus_view = stimulus_view

        self.connect_data_signals()
        self._on_model_stim_config_changed()

    def connect_data_signals(self):
        """Data signals are owned by feature controllers."""
        self.stimulus_view.stimulusChanged.connect(self._on_view_stim_config_changed)
        self.app_model.stim_config_changed.connect(self._on_model_stim_config_changed)
        self.stimulus_view.stepChanged.connect(self.update_plot)
        self.stimulus_view.stimulusHighlightChanged.connect(self.update_plot)
        self.stimulus_view.voltageBoundaryChanged.connect(self.update_plot)
        self.stimulus_view.previewPulseClicked.connect(
            self.stimulus_view.ui.segmentTabWidget.setCurrentIndex
        )
        self.stimulus_view.start_handle.dragged.connect(self._drag_pulse_start)
        self.stimulus_view.end_handle.dragged.connect(self._drag_pulse_end)
        for handle in (self.stimulus_view.start_handle, self.stimulus_view.end_handle):
            handle.sigPositionChangeFinished.connect(self._finish_pulse_drag)

    def _finish_pulse_drag(self, *_):
        """Refresh handle visibility without changing the user's view on release."""
        self.update_plot()

    def _on_model_stim_config_changed(self):
        """Refresh the preview and fit its axes when the sequence changes."""
        # Drag edits already update the open tab. Keep the axes still under the pointer.
        dragging = (
            self.stimulus_view.start_handle.moving
            or self.stimulus_view.end_handle.moving
        )
        if not dragging:
            self.update_ui_from_model()
        self.update_plot()
        if not dragging:
            self._fit_preview_axes()

    def _fit_preview_axes(self, *_):
        # Use bounds across every stimulus so stepping preserves the voltage scale.
        generator = self.app_model.stim_generator
        _, peak_v = self.app_model.get_y_bounds()
        limit_v = generator.config.limit_v
        span_v = min(peak_v, limit_v) if peak_v else limit_v
        self.stimulus_view.plotWidget.setXRange(*self.app_model.get_x_bounds())
        self.stimulus_view.plotWidget.setYRange(-span_v, span_v)

    def _drag_pulse_start(self, position: QPointF) -> None:
        tab = self.stimulus_view.ui.segmentTabWidget.currentWidget()
        if not isinstance(tab, PulseTabView):
            return
        step = self.stimulus_view.ui.stepSlider.value()
        spins = tab.spinboxes
        limit = self.app_model.stim_generator.config.limit_v
        height = max(-limit, min(position.y(), limit))
        if not tab.monophasic_checkbox.isChecked():
            # A biphasic pulse has a positive top even if its first phase is negative.
            first_phase = spins["amp_v"].value() + step * spins["step_amp_v"].value()
            height = max(0.0, height) * (-1 if first_phase < 0 else 1)
        self._set_pulse_fields(
            tab,
            start_s=position.x() - step * spins["step_start_s"].value(),
            amp_v=height - step * spins["step_amp_v"].value(),
        )

    def _drag_pulse_end(self, position: QPointF) -> None:
        tab = self.stimulus_view.ui.segmentTabWidget.currentWidget()
        if not isinstance(tab, PulseTabView):
            return
        step = self.stimulus_view.ui.stepSlider.value()
        spins = tab.spinboxes
        # Convert the dragged endpoint at this step back to the base duration.
        start_s = spins["start_s"].value() + step * spins["step_start_s"].value()
        self._set_pulse_fields(
            tab, dur_s=position.x() - start_s - step * spins["step_dur_s"].value()
        )

    def _set_pulse_fields(self, tab: PulseTabView, **values: float) -> None:
        """Let the spin boxes clamp and round a drag, then publish one update."""
        with Blocker(tab):
            for field, value in values.items():
                tab.spinboxes[field].setValue(value)
        tab.segmentChanged.emit()

    def _on_view_stim_config_changed(self):
        """Update stimulus model data from the stimulus view and refresh the plot."""
        segments = []

        tab_widget = self.stimulus_view.ui.segmentTabWidget

        for i in range(tab_widget.count()):
            widget = tab_widget.widget(i)
            if isinstance(widget, PulseTabView):
                segments.append(
                    {
                        name: round(spin.value(), DOUBLE_SPIN_PARSE_ROUND_DECIMALS)
                        for name, spin in widget.spinboxes.items()
                    }
                    | {"is_monophasic": widget.monophasic_checkbox.isChecked()},
                )

        pulses = [Pulse(**segment) for segment in segments]
        stim_config = StimulusConfig(
            pulses=pulses,
            n_steps=self.stimulus_view.ui.nSpinBox.value(),
            dur_s=self.stimulus_view.ui.durSpinBox.value(),
            limit_v=DEFAULT_LIMIT_V,
        )

        self.app_model.update_stim_config(stim_config)

    def update_ui_from_model(self):
        """Update stimulus view parameter fields from the stimulus model."""
        stim_config = self.app_model.stim_generator.config
        tab_widget = self.stimulus_view.ui.segmentTabWidget
        prev_index = tab_widget.currentIndex()

        # Clamp the selected step before drawing against the new sequence.
        with Blocker(self.stimulus_view, self.stimulus_view.ui.stepSlider):
            self.stimulus_view.update_step_slider(stim_config.n_steps)
            self.stimulus_view.ui.durSpinBox.setValue(stim_config.stim.dur_s)
            self.stimulus_view.ui.nSpinBox.setValue(stim_config.n_steps)

            # Remove all tabs first
            while tab_widget.count() > 0:
                tab_widget.removeTab(0)

            # Generate as many tabs as needed
            while tab_widget.count() < len(stim_config.stim.pulses):
                self.stimulus_view.add_segment_tab()

            for i, pulse in enumerate(stim_config.stim.pulses):
                widget = tab_widget.widget(i)
                if not isinstance(widget, PulseTabView):
                    continue

                widget.spinboxes["amp_v"].setValue(pulse.amp_v)
                widget.spinboxes["start_s"].setValue(pulse.start_s)
                widget.spinboxes["dur_s"].setValue(pulse.dur_s)
                widget.spinboxes["step_amp_v"].setValue(pulse.step_amp_v)
                widget.spinboxes["step_start_s"].setValue(pulse.step_start_s)
                widget.spinboxes["step_dur_s"].setValue(pulse.step_dur_s)
                widget.monophasic_checkbox.setChecked(pulse.is_monophasic)

            if tab_widget.count() > 0:
                restore_index = min(max(prev_index, 0), tab_widget.count() - 1)
                tab_widget.setCurrentIndex(restore_index)

    def update_plot(self, *_):
        """Draw the selected step without changing the preview axes."""
        self.stimulus_view.clear_plot()
        self.stimulus_view.hide_pulse_handles()
        self.stimulus_view.draw_zero_line()

        if self.stimulus_view.ui.show_voltage_boundary_checkbox.isChecked():
            self.stimulus_view.draw_voltage_limit(
                self.app_model.stim_generator.config.limit_v
            )

        target_dur = self.app_model.stim_generator.config.stim.dur_s
        train_plot_sr = TARGET_N_SAMPLES_PULSE_PLOT / target_dur

        cur_step = self.stimulus_view.ui.stepSlider.value()
        y, t = self.app_model.stim_generator.sample_at_idx(train_plot_sr, cur_step)
        self.stimulus_view.update_train_plot((t, y), color="k", width=1)
        stimulus = self.app_model.stim_generator.stims[cur_step]
        intervals = []
        for pulse in stimulus.pulses:
            _, start, count = stimulus.pulse_overlap(pulse, train_plot_sr)
            intervals.append((start / train_plot_sr, (start + count) / train_plot_sr))
        self.stimulus_view.preview_view_box.pulse_intervals = intervals

        cur_tab = self.stimulus_view.ui.segmentTabWidget.currentIndex()
        pulses = stimulus.pulses
        if (
            self.stimulus_view.ui.highlight_selected_pulse_checkbox.isChecked()
            and 0 <= cur_tab < len(pulses)
        ):
            pulse = pulses[cur_tab]
            if pulse.dur_s <= 0:
                if 0 <= pulse.start_s <= target_dur:
                    # A collapsed pulse has only an endpoint at its configured start.
                    self.stimulus_view.start_handle.hide()
                    self.stimulus_view.show_duration_handle(pulse.start_s)
            else:
                self._plot_highlighted_pulse(pulse, train_plot_sr, cur_step, cur_tab)

        self.stimulus_view.show_step_position(
            cur_step, self.app_model.stim_generator.config.n_steps
        )

    def _plot_highlighted_pulse(
        self, pulse: Pulse, sample_rate: float, step: int, tab: int
    ) -> None:
        """Draw the visible pulse samples and their editing controls."""
        generator = self.app_model.stim_generator
        y, t = generator.sample_at_idx(sample_rate, step, tab)
        self.stimulus_view.update_train_plot((t, y), color="b", width=2)
        if not t.size:
            return

        # The end boundary is one sample interval beyond the last visible sample.
        end_s = t[-1] + 1 / sample_rate
        self.stimulus_view.draw_segment_bounds(t[0], end_s)
        limit = generator.config.limit_v
        level = max(-limit, min(pulse.amp_v, limit))
        top_v = level if pulse.is_monophasic else abs(level)
        self.stimulus_view.position_pulse_handles(t[0], end_s, top_v)
