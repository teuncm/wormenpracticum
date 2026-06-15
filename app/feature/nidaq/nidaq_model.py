from app.feature.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from PySide6.QtCore import QObject, Signal


class NidaqModel(QObject):
    device_name: str | None
    device_status: str

    discovery_state_changed = Signal()

    # daq_settings = {
    #     # identity
    #     "device_name": device.name,
    #     "board_name": device.product_type,
    #     # hardware capabilities
    #     "ai_channel_count": len(device.ai_physical_chans),
    #     "ao_channel_count": len(device.ao_physical_chans),
    #     "ai_resolution": ai_channel.ai_resolution,
    #     "ao_resolution": ao_channel.ao_resolution,
    #     "ai_min_rate": device.ai_min_rate,
    #     "ai_max_single_chan_rate": device.ai_max_single_chan_rate,
    #     "ai_max_multi_chan_rate": device.ai_max_multi_chan_rate,
    #     "ao_min_rate": device.ao_min_rate,
    #     "ao_max_rate": device.ao_max_rate,
    #     "ai_range_high": ai_channel.ai_rng_high,
    #     "ao_range_high": ao_channel.ao_dac_rng_high,
    #     # app settings
    #     "ai_rate": ai_rate,
    #     "ao_rate": ao_rate,
    #     "ai_voltage_range": tuple(ai_voltage_range),
    #     "ao_voltage_range": tuple(ao_voltage_range),
    #     "output_duration": output_duration,
    #     # routing settings
    #     "positive_channel": 0,
    #     "negative_channel": 0,
    #     "routing_word": 0,
    #     "routing_flags": 128,
    #     # digital port names
    #     "routing_select_port": f"{device.name}/port0",
    #     "routing_flag_port": f"{device.name}/port2",
    # }

    def __init__(self):
        super().__init__()

        self.device_name = None
        self.device_status = NI_DAQ_UNAVAILABLE_STATUS

    def set_discovery_state(self, device_name, status):
        self.device_name = device_name
        self.device_status = status

        self.discovery_state_changed.emit()
