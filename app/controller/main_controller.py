from app.model.main_model import MainModel
from app.view.main_view import MainView
from app.view.pulse_view import PulseView


class MainController:
    def __init__(self):
        self.main_model = MainModel()
        self.main_view = MainView()
        self.pulse_view = PulseView()

    def show(self):
        self.main_view.show()
        self.pulse_view.show()
