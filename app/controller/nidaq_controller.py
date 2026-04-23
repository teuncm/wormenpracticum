import numpy as np
from app.model.nidaq.nidaq_constants import NI_DAQ_UNAVAILABLE_STATUS
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx.system import System
from nidaqmx.task import Task


class NidaqController:
    def __init__(self, nidaq_model):
        self.nidaq_model = nidaq_model

    def discover(self) -> bool:
        """Discover NI-DAQ devices and update model state accordingly."""
        print("Discovering...")
        try:
            system = System.local()
        except Exception as exc:
            self.nidaq_model.set_discovery_state(None, str(exc))
            return False

        for device in system.devices:
            if len(device.ao_physical_chans) > 0:
                self.nidaq_model.set_discovery_state(
                    device.name, f"NI-DAQ device ready: {device.name}"
                )
                return True

        self.nidaq_model.set_discovery_state(None, NI_DAQ_UNAVAILABLE_STATUS)
        return False

    def execute(self):
        sr = 1000
        n_samples = 200

        waveform = np.array(
            [0.5 * (1 + np.sin(2 * np.pi * 5 * t / sr)) for t in range(n_samples)]
        )

        routing_word, routing_flags = self.generate_routing_mask(
            positive_channel=3,
            negative_channel=4,
        )

        with Task() as digital_output_task, Task() as ai_task, Task() as ao_task:
            digital_output_task.do_channels.add_do_chan(
                f"{self.nidaq_model.device_name}/port0"
            )
            digital_output_task.do_channels.add_do_chan(
                f"{self.nidaq_model.device_name}/port2"
            )

            digital_output_task.write([routing_word, routing_flags])

            # Measurement is mapped 1:1 to ai
            ai_task.ai_channels.add_ai_voltage_chan(
                f"{self.nidaq_model.device_name}/ai4:6"
            )

            # Stimulation goes to ao0 and ao1, matching the MATLAB app's use of two channels for differential output.
            ao_task.ao_channels.add_ao_voltage_chan(
                f"{self.nidaq_model.device_name}/ao0:1"
            )

            ao_data = np.zeros((2, n_samples))
            ao_data[0, :] = waveform
            ao_data[1, :] = -waveform

            ai_data = np.zeros((3, n_samples))

            # AO = master
            ao_task.timing.cfg_samp_clk_timing(
                rate=sr,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=n_samples,
            )

            # AI follows AO sample clock
            ai_task.timing.cfg_samp_clk_timing(
                rate=sr,  # with external clock, this is the expected max rate
                source=f"/{self.nidaq_model.device_name}/ao/SampleClock",
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=n_samples,
            )

            # shared start trigger
            ai_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                f"/{self.nidaq_model.device_name}/ao/StartTrigger"
            )

            # preload AO data
            writer = AnalogMultiChannelWriter(ao_task.out_stream)
            reader = AnalogMultiChannelReader(ai_task.in_stream)

            writer.write_many_sample(ao_data)

            ai_task.start()
            ao_task.start()

            reader.read_many_sample(
                ai_data,
                number_of_samples_per_channel=n_samples,
                timeout=2.0,
            )

            ao_task.wait_until_done(timeout=2.0)

    def magic(self):
        if self.discover():
            self.execute()

    def generate_routing_mask(
        self, positive_channel: int, negative_channel: int
    ) -> tuple[int, int]:
        """
        Convert selected stimulation channels into the two routing bytes
        expected by the UvA routing hardware.

        Returns:
            routing_word: selector byte for the two stim channels
            routing_flags: control/enable byte
        """
        if not (1 <= positive_channel <= 16):
            raise ValueError("positive_channel must be in 1..16")
        if not (1 <= negative_channel <= 16):
            raise ValueError("negative_channel must be in 1..16")
        if positive_channel == negative_channel:
            raise ValueError("positive_channel and negative_channel must differ")

        # MATLAB: nulcode = 16 + 32 + 64 + 128 = 240
        routing_flags = 0b11110000
        routing_word = 0

        # Positive stim goes in low nibble
        if positive_channel > 1:
            routing_word += positive_channel - 1
            routing_flags -= 32  # clear bit 5

        # Negative stim goes in high nibble
        if negative_channel > 1:
            routing_word += (negative_channel - 1) * 16
            routing_flags -= 64  # clear bit 6

        # Keep bit 7 on, matching the MATLAB logic
        if routing_flags < 128:
            routing_flags += 128

        return routing_word, routing_flags
