from app.controller.nidaq.connect import get_first_ai_device
from app.model.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS


class NidaqModel:
    nidaq_discovered: bool
    nidaq_device_name: str | None
    nidaq_status: str

    def __init__(self):
        self.nidaq_discovered = False
        self.nidaq_device_name = None
        self.nidaq_status = NI_DAQ_UNAVAILABLE_STATUS

    def discover_first_ai_device(self):
        self.refresh_discovery_status()
        return {
            "discovered": self.nidaq_discovered,
            "device_name": self.nidaq_device_name,
            "status": self.nidaq_status,
        }

    def refresh_discovery_status(self):
        try:
            device_name = get_first_ai_device()
        except Exception as exc:
            self.set_discovery_state(False, None, f"NI-DAQ discovery error: {exc}")
            return self.nidaq_status

        if device_name is None:
            self.set_discovery_state(False, None, NI_DAQ_UNAVAILABLE_STATUS)
            return self.nidaq_status

        self.set_discovery_state(True, device_name, f"NI-DAQ ready: {device_name}")
        return self.nidaq_status

    def set_discovery_state(self, discovered, device_name, status):
        self.nidaq_discovered = discovered
        self.nidaq_device_name = device_name
        self.nidaq_status = status
