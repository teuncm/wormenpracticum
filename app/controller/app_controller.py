from app.constants import DOUBLE_SPIN_PARSE_ROUND_DECIMALS, TARGET_N_SAMPLES_PULSE_PLOT
from app.model.app_model import AppModel
from app.model.nidaq_constants import NI_DAQ_DISCOVERY_POLL_INTERVAL_MS
from app.model.nidaq_model import NidaqModel
from app.view.about_view import AboutView
from app.view.analyze_view import AnalyzeView
from app.view.main_view import MainView
from app.view.protocol_view import ProtocolView
from app.view.pulse_segment import PulseSegmentWidget
from app.view.pulse_view import PulseView
from app.view.smooth_view import SmoothView
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


class AppController:
    def __init__(self):
        self.app_model = AppModel()
        self.nidaq_model = NidaqModel()

        self.main_view = MainView()
        self.pulse_view = PulseView()
        self.protocol_view = ProtocolView()
        self.about_view = AboutView()
        self.analyze_view = AnalyzeView()
        self.smooth_view = SmoothView()

        self.pulse_view.pulseChanged.connect(self.update_pulse_state)
        self.pulse_view.stepChanged.connect(self.update_plot)
        self.pulse_view.pulseHighlightChanged.connect(self.update_plot)

        self.refresh_nidaq_status()
        self.nidaq_status_timer = QTimer(self.main_view)
        self.nidaq_status_timer.setInterval(NI_DAQ_DISCOVERY_POLL_INTERVAL_MS)
        self.nidaq_status_timer.timeout.connect(self.refresh_nidaq_status)
        self.nidaq_status_timer.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

        self.refresh_nidaq_status()
        self.nidaq_status_timer = QTimer(self.main_view)
        self.nidaq_status_timer.setInterval(NI_DAQ_DISCOVERY_POLL_INTERVAL_MS)
        self.nidaq_status_timer.timeout.connect(self.refresh_nidaq_status)
        self.nidaq_status_timer.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

        self.connect_open_signals()

    def connect_open_signals(self):
        self.main_view.ui.actionAbout.triggered.connect(self.about_view.show)
        self.main_view.ui.actionAnalyze.triggered.connect(self.analyze_view.show)
        self.main_view.ui.actionSmoothing.triggered.connect(self.smooth_view.show)
        self.main_view.editImpulseRequested.connect(self.pulse_view.show)
        self.main_view.editProtocolRequested.connect(self.protocol_view.show)

    def start(self):
        self.main_view.show()

    def refresh_nidaq_status(self):
        self.nidaq_model.refresh_discovery_status()
        self.main_view.set_nidaq_status(self.nidaq_model.nidaq_status)

    def shutdown(self):
        self.nidaq_status_timer.stop()

    def update_pulse_state(self):
        """Update pulse data and plot"""
        segments = []

        tab_widget = self.pulse_view.ui.segmentTabWidget

        for i in range(tab_widget.count()):
            widget = tab_widget.widget(i)
            if isinstance(widget, PulseSegmentWidget):
                segments.append(
                    {
                        name: round(spin.value(), DOUBLE_SPIN_PARSE_ROUND_DECIMALS)
                        for name, spin in widget.spinboxes.items()
                    }
                    | {"is_monophasic": widget.monophasic_checkbox.isChecked()},
                )

        params = {
            "N": self.pulse_view.ui.nSpinBox.value(),
            "dur_s": self.pulse_view.ui.durSpinBox.value(),
            "limit_v": self.pulse_view.ui.limitSpinBox.value(),
            "segments": segments,
        }

        self.app_model.update_pulse_config(params)
        self.pulse_view.update_step_slider(params["N"])

    def update_plot(self, *_):
        if self.app_model.stimulus_generator is None:
            return

        self.pulse_view.clear_plot()
        self.pulse_view.draw_zero_line()

        self.pulse_view.draw_voltage_limit(
            self.app_model.stimulus_generator.config.limit_v
        )

        target_dur = self.app_model.stimulus_generator.config.stim.dur_s
        train_plot_sr = TARGET_N_SAMPLES_PULSE_PLOT / target_dur

        # Draw the stimulus
        cur_step = self.pulse_view.ui.stepSlider.value()
        y, t = self.app_model.stimulus_generator.sample_at_idx(train_plot_sr, cur_step)
        self.pulse_view.update_train_plot((t, y), color="k", width=1)

        # Optionally draw the pulse
        if self.pulse_view.highlightPulseCheckbox.isChecked():
            cur_tab = self.pulse_view.ui.segmentTabWidget.currentIndex()
            current_pulse = self.app_model.stimulus_generator.stims[cur_step].pulses[
                cur_tab
            ]
            y, t = self.app_model.stimulus_generator.sample_at_idx(
                train_plot_sr, cur_step, cur_tab
            )
            self.pulse_view.update_train_plot((t, y), color="b", width=2)

            if len(t) > 0 and len(y) > 0:
                center = None
                if not current_pulse.is_monophasic:
                    center = (t[0] + t[-1]) / 2

                self.pulse_view.draw_pulse_bounds(t[0], t[-1], y.max(), y.min(), center)

        # Set plot boundaries based on the signal.
        x_bounds = self.app_model.get_x_bounds()
        y_bounds = self.app_model.get_y_bounds()

        if x_bounds is not None and y_bounds is not None:
            self.pulse_view.plotWidget.setXRange(*x_bounds)
            self.pulse_view.plotWidget.setYRange(*y_bounds)

        self.pulse_view.plotWidget.setTitle(f"Stimulus {cur_step + 1}")
