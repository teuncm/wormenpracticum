from app.view.main_view import MainView
from app.view.pulse_view import PulseView


class MainController:
    def __init__(self):
        self.view = MainView()
        self.view.set_controller(self)

        self.pulse_view = PulseView()

    def start(self):
        self.view.show()
        # self.pulse_view.show()
