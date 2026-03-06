import app.model.signal
from app.model.app_model import AppModel
from app.view.main_view import MainView
from app.view.pulse_segment import PulseSegmentWidget
from app.view.pulse_view import PulseView

SEGMENT_ROUND_DECIMALS = 5


class AppController:
    def __init__(self):
        self.app_model = AppModel()

        self.main_view = MainView()
        self.pulse_view = PulseView()

        self.main_view.editImpulseRequested.connect(self.open_impulse_window)
        self.pulse_view.pulseChanged.connect(self.update_pulse_state)
        self.pulse_view.stepChanged.connect(self.update_plot)

    def start(self):
        self.main_view.show()

    def open_impulse_window(self):
        self.pulse_view.show()

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

        cur_step = self.pulse_view.ui.stepSlider.value()

        sr_hz = 1000
        signal_obj, sample_offset = self.app_model.pulse_generator.get_signal(
            sr_hz, cur_step
        )
        y = signal_obj.sample(sr_hz)
        t = app.model.signal.get_timeframe_s(len(y), sr_hz, sample_offset)

        self.pulse_view.clear_plot()
        self.pulse_view.update_pulse_plot((t, y), color="k", width=1)

        cur_tab = self.pulse_view.ui.segmentTabWidget.currentIndex()

        sr_hz = 1000
        signal_obj, sample_offset = self.app_model.pulse_generator.get_signal(
            sr_hz, cur_step, cur_tab
        )
        y = signal_obj.sample(sr_hz)
        t = app.model.signal.get_timeframe_s(len(y), sr_hz, sample_offset)

        self.pulse_view.update_pulse_plot((t, y), color="b", width=3)

        # Set plot boundaries based on the signal.
        x_bounds = self.app_model.get_x_bounds()
        y_bounds = self.app_model.get_y_bounds()

        if x_bounds is not None and y_bounds is not None:
            self.pulse_view.plotWidget.setXRange(*x_bounds)
            self.pulse_view.plotWidget.setYRange(*y_bounds)

        self.pulse_view.plotWidget.setTitle(f"Step {cur_step + 1}")
