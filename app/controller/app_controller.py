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
                )

        params = {"N": self.pulse_view.ui.nSpinBox.value(), "segments": segments}

        self.app_model.update_pulse_config(params)
        vs = self.app_model.sample_pulse(1000)
        if vs is not None and self.app_model.pulse_config is not None:
            ts = self.app_model.pulse_config.get_timeframe_s(vs, 1000)
            self.pulse_view.update_pulse_plot((ts, vs))
