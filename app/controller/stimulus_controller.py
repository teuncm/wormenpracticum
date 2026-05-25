from app.constants import DOUBLE_SPIN_PARSE_ROUND_DECIMALS, TARGET_N_SAMPLES_PULSE_PLOT
from app.model.app_model import AppModel
from app.model.config.stimulus_config import StimulusConfig
from app.model.stimulus.pulse import Pulse
from app.view.pulse_tab_view import PulseTabView
from app.view.stimulus_view import StimulusView
from app.view.view_helpers import Blocker


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

    def _on_model_stim_config_changed(self):
        # Reflect model change in view parameter fields
        self.update_ui_from_model()

        # Reflect model change in plot
        self.update_plot()

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
            limit_v=self.stimulus_view.ui.limitSpinBox.value(),
        )

        self.app_model.update_stim_config(stim_config)
        self.stimulus_view.update_step_slider(stim_config.n_steps)

    def update_ui_from_model(self):
        """Update stimulus view parameter fields from the stimulus model."""
        stim_config = self.app_model.stim_generator.config
        tab_widget = self.stimulus_view.ui.segmentTabWidget
        prev_index = tab_widget.currentIndex()

        with Blocker(self.stimulus_view):
            self.stimulus_view.ui.durSpinBox.setValue(stim_config.stim.dur_s)
            self.stimulus_view.ui.nSpinBox.setValue(stim_config.n_steps)
            self.stimulus_view.ui.limitSpinBox.setValue(stim_config.limit_v)

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
        self.stimulus_view.clear_plot()
        self.stimulus_view.draw_zero_line()

        self.stimulus_view.draw_voltage_limit(
            self.app_model.stim_generator.config.limit_v
        )

        target_dur = self.app_model.stim_generator.config.stim.dur_s
        train_plot_sr = TARGET_N_SAMPLES_PULSE_PLOT / target_dur

        cur_step = self.stimulus_view.ui.stepSlider.value()
        y, t = self.app_model.stim_generator.sample_at_idx(train_plot_sr, cur_step)
        self.stimulus_view.update_train_plot((t, y), color="k", width=1)

        if self.stimulus_view.ui.highlight_selected_pulse_checkbox.isChecked():
            cur_tab = self.stimulus_view.ui.segmentTabWidget.currentIndex()
            current_pulse = self.app_model.stim_generator.stims[cur_step].pulses[
                cur_tab
            ]
            y, t = self.app_model.stim_generator.sample_at_idx(
                train_plot_sr, cur_step, cur_tab
            )
            self.stimulus_view.update_train_plot((t, y), color="b", width=2)

            if len(t) > 0 and len(y) > 0:
                center = None
                if not current_pulse.is_monophasic:
                    center = (t[0] + t[-1]) / 2

                self.stimulus_view.draw_segment_bounds(
                    t[0], t[-1], y.max(), y.min(), center
                )

        x_bounds = self.app_model.get_x_bounds()
        y_bounds = self.app_model.get_y_bounds()

        if x_bounds is not None and y_bounds is not None:
            self.stimulus_view.plotWidget.setXRange(*x_bounds)
            self.stimulus_view.plotWidget.setYRange(*y_bounds)

        self.stimulus_view.plotWidget.setTitle(f"Stimulus {cur_step + 1}")
