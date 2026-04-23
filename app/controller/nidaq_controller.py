from app.model.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from nidaqmx.system import System
from nidaqmx.task import Task


class NidaqController:
    def __init__(self, nidaq_model):
        self.nidaq_model = nidaq_model

    def discover(self) -> bool:
        """Discover NI-DAQ devices and update model state accordingly."""
        try:
            system = System.local()
        except Exception as exc:
            print(f"NI-DAQ discovery failed: {exc}")
            self.nidaq_model.set_discovery_state(None, NI_DAQ_UNAVAILABLE_STATUS)
            return False

        for device in system.devices:
            if len(device.ao_physical_chans) > 0:
                print(f"Found NI-DAQ output device: {device.name}")
                self.nidaq_model.set_discovery_state(
                    device.name, f"NI-DAQ ready: {device.name}"
                )
                return True

        print("No NI-DAQ output devices found.")
        self.nidaq_model.set_discovery_state(None, NI_DAQ_UNAVAILABLE_STATUS)
        return False

    def execute(self):
        pass
        # with nidaqmx.Task() as ai_task, nidaqmx.Task() as ao_task:
        #     # channels
        #     ai_task.ai_channels.add_ai_voltage_chan(f"{dev}/ai0:13")
        #     ao_task.ao_channels.add_ao_voltage_chan(f"{dev}/ao0:1")

        #     # AO = master
        #     ao_task.timing.cfg_samp_clk_timing(
        #         rate=ao_rate,
        #         sample_mode=AcquisitionType.FINITE,
        #         samps_per_chan=n_ao,
        #     )

        #     # AI follows AO sample clock
        #     ai_task.timing.cfg_samp_clk_timing(
        #         rate=ao_rate,  # with external clock, this is the expected max rate
        #         source=f"/{dev}/ao/SampleClock",
        #         sample_mode=AcquisitionType.FINITE,
        #         samps_per_chan=n_ai,
        #     )

        #     # shared start trigger
        #     ai_task.triggers.start_trigger.cfg_dig_edge_start_trig(
        #         f"/{dev}/ao/StartTrigger"
        #     )

        #     # preload AO data
        #     writer = AnalogMultiChannelWriter(ao_task.out_stream, auto_start=False)
        #     writer.write_many_sample(ao_waveform)

        #     # arm follower first
        #     ai_task.start()
        #     ao_task.start()  # AO start trigger fires, both begin together

    def magic(self):
        self.discover()
        pass
