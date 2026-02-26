from app.model.app_model import AppModel
from app.view.main_view import MainView
from app.view.pulse_view import PulseView


class AppController:
    def __init__(self):
        self.app_model = AppModel()

        self.main_view = MainView()
        self.pulse_view = PulseView()

        self.main_view.editImpulseRequested.connect(self.open_impulse_window)
        self.pulse_view.pulseParametersChanged.connect(self.update_model_from_view)

    def start(self):
        self.main_view.show()

    def open_impulse_window(self):
        self.pulse_view.show()

    def update_model_from_view(self):
        params = {
            name: spin.value() for name, spin in self.pulse_view.spinboxes.items()
        }

        print(params)

        # self.app_model.update(**params)
        # self.update_plot()
