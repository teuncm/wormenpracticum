from app.view.pulse_view import PulseView


class MainController:
    def __init__(self, model, view):
        self.model = model
        self.model.set_controller(self)
        self.view = view
        self.view.set_controller(self)

        self.pulse_view = PulseView()

    def start(self):
        self.view.show()
        self.pulse_view.show()
