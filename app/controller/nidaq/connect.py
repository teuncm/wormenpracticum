
from nidaqmx.system import System
from nidaqmx.task import Task


def get_first_ai_device():
    system = System.local()

    for device in system.devices:
        if len(device.ai_physical_chans) > 0:
            return device.name

    return None


def get_first_ai_channel():
    system = System.local()

    for device in system.devices:
        if len(device.ai_physical_chans) > 0:
            return device.ai_physical_chans.channel_names[0]

    return None


def get_ao_channel_names():
    system = System.local()
    channel_names = []

    for device in system.devices:
        if len(device.ao_physical_chans) > 0:
            channel_names.extend(device.ao_physical_chans.channel_names)

    return channel_names


def get_digital_line_names():
    system = System.local()
    channel_names = []
    seen = set()

    for device in system.devices:
        for collection_name in ("di_lines", "do_lines"):
            collection = getattr(device, collection_name, None)
            if collection is None:
                continue

            for channel_name in collection.channel_names:
                if channel_name in seen:
                    continue

                seen.add(channel_name)
                channel_names.append(channel_name)

    return channel_names


def connect_first_ai_task():
    """Create a real NI-DAQ task on the first available analog input channel.

    Returns a dict with the connection outcome so the UI can display a clear
    status message without needing to know the NI-DAQ library details.
    """
    try:
        channel_name = get_first_ai_channel()
    except Exception as exc:  # pragma: no cover - depends on local NI-DAQ setup
        return {
            "connected": False,
            "task": None,
            "device_name": None,
            "channel_name": None,
            "status": f"NI-DAQ error: {exc}",
        }

    if channel_name is None:
        return {
            "connected": False,
            "task": None,
            "device_name": None,
            "channel_name": None,
            "status": "No NI-DAQ device with analog input channels found",
        }

    task = Task()

    try:
        task.ai_channels.add_ai_voltage_chan(channel_name)
    except Exception as exc:  # pragma: no cover - depends on local NI-DAQ setup
        task.close()
        return {
            "connected": False,
            "task": None,
            "device_name": None,
            "channel_name": None,
            "status": f"Failed to create NI-DAQ task on {channel_name}: {exc}",
        }

    device_name = channel_name.split("/")[0]

    return {
        "connected": True,
        "task": task,
        "device_name": device_name,
        "channel_name": channel_name,
        "status": f"Connected to {channel_name}",
    }
