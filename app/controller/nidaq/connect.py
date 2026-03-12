
from nidaqmx.system import System


def get_first_ai_device():
    system = System.local()

    for device in system.devices:
        if len(device.ai_physical_chans) > 0:
            return device.name

    return None
