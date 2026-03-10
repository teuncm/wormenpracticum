from app.model.app_model import AppModel
from app.view.main_view import MainView
from app.view.protocol_view import ProtocolView
from app.view.pulse_segment import PulseSegmentWidget
from app.view.pulse_view import PulseView

SEGMENT_ROUND_DECIMALS = 5
TARGET_N_SAMPLES = 2001


class AppController:
    def __init__(self):
        self.app_model = AppModel()

        self.main_view = MainView()
        self.pulse_view = PulseView()
        self.protocol_view = ProtocolView()

        self.main_view.editImpulseRequested.connect(self.open_impulse_window)
        self.main_view.editProtocolRequested.connect(self.open_protocol_window)
        self.pulse_view.pulseChanged.connect(self.update_pulse_state)
        self.pulse_view.stepChanged.connect(self.update_plot)

    def start(self):
        self.main_view.show()

    def open_impulse_window(self):
        self.pulse_view.show()

    def open_protocol_window(self):
        self.protocol_view.show()

    def update_pulse_state(self):
        """Update pulse data and plot"""
        segments = []

        tab_widget = self.pulse_view.ui.segmentTabWidget

        for i in range(tab_widget.count()):
            widget = tab_widget.widget(i)
            if isinstance(widget, PulseSegmentWidget):
                segments.append(
                    {
                        name: round(spin.value(), SEGMENT_ROUND_DECIMALS)
                        for name, spin in widget.spinboxes.items()
                    }
                    | {"is_monophasic": widget.monophasic_checkbox.isChecked()},
                )

        params = {"N": self.pulse_view.ui.nSpinBox.value(), "segments": segments}

        self.app_model.update_pulse_config(params)
        self.pulse_view.update_step_slider(params["N"])

    def update_plot(self):
        if self.app_model.pulse_generator is None:
            return

        self.pulse_view.clear_plot()
        self.pulse_view.draw_zero_line()

        # Early exit if duration is 0!
        target_dur = self.app_model.pulse_generator.target_dur_s()
        if target_dur == 0:
            return

        train_plot_sr = TARGET_N_SAMPLES / target_dur

        cur_step = self.pulse_view.ui.stepSlider.value()
        y, t = self.app_model.pulse_generator.sample_section(train_plot_sr, cur_step)
        self.pulse_view.update_train_plot((t, y), color="k", width=1)

        cur_tab = self.pulse_view.ui.segmentTabWidget.currentIndex()
        y, t = self.app_model.pulse_generator.sample_section(
            train_plot_sr, cur_step, cur_tab
        )
        self.pulse_view.update_train_plot((t, y), color="b", width=2)

        if len(t) > 0 and len(y) > 0:
            self.pulse_view.draw_pulse_bounds(t[0], t[-1], y.max(), y.min())

        # Set plot boundaries based on the signal.
        x_bounds = self.app_model.get_x_bounds()
        y_bounds = self.app_model.get_y_bounds()

        if x_bounds is not None and y_bounds is not None:
            self.pulse_view.plotWidget.setXRange(*x_bounds)
            self.pulse_view.plotWidget.setYRange(*y_bounds)

        self.pulse_view.plotWidget.setTitle(f"Step {cur_step + 1}")
