import nidaqmx
import nidaqmx.system
from nidaqmx.system import System
from nidaqmx.constants import AcquisitionType, VoltageUnits, TerminalConfiguration, LineGrouping
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter
import numpy as np
from scipy.signal import convolve



def check_if_device_is_connected():
    system = nidaqmx.system.System.local()
    try:
        deviceName = system.devices[0].name
    except:
        return None
    return deviceName

def get_device_info():
    system = nidaqmx.system.System.local()
    device = system.devices[0]
    
    Device = {}
    Device['name'] = device.name
    
    # Analog Input Configuration
    ai_task = nidaqmx.Task()
    ai_channel = ai_task.ai_channels.add_ai_voltage_chan(f"{device.name}/ai0", terminal_config=TerminalConfiguration.RSE)
    Device['adcresolution'] = ai_channel.ai_resolution
    Device['adcmax'] = device.ai_physical_chans.__len__()
    Device['adcminrate'] = device.ai_min_rate
    Device['adcmaxrate'] = ai_channel.ai_max
    
    # both two are not the standard variables
    Device['adcranges'] = ai_channel.ai_rng_high
    # Device['adcgains'] = ai_channel.ai_gain
    
    # Analog Output Configuration
    ao_task = nidaqmx.Task()
    ao_channel = ao_task.ao_channels.add_ao_voltage_chan(f"{device.name}/ao0")
    Device['dacresolution'] = ao_channel.ao_resolution
    Device['dacmax'] = device.ao_physical_chans.__len__()
    Device['dacminrate'] = device.ao_min_rate
    Device['dacmaxrate'] = device.ao_max_rate
    # not standard variable
    Device['dacranges'] = ao_channel.ao_dac_rng_high
    
    Device['yrange'] = [-10, 10]
    Device['ymax'] = [y * 1000 / 500 for y in Device['yrange']]
    Device['dacrate'] = 500000
    Device['adcrate'] = 250000 / 16
    
    # Digital I/O Configuration
    # Digital Input Configuration
    di_task = nidaqmx.Task()
    Device['lines1'] = di_task.di_channels.add_di_chan(f"{device.name}/port0/line0:7", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
    Device['lines2'] = di_task.di_channels.add_di_chan(f"{device.name}/port1/line0:7", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
    
    # Digital Output Configuration
    do_task = nidaqmx.Task()
    Device['lines3'] = do_task.do_channels.add_do_chan(f"{device.name}/port2/line0:7", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
    Device['lines'] = [Device['lines1'], Device['lines3']]
    Device['len'] = len(Device['lines'])
    Device['val1'] = 0
    Device['val3'] = 128
    
    # Print Device Information
    print(f"Device = {device.product_type} Boardname = {Device['name']}")
    print(f"   ADC-channels {Device['adcmax']:02d}  {Device['adcmaxrate'] / 1000:.0f} kHz")
    print(f"   DAC-channels {Device['dacmax']:02d}  {Device['dacmaxrate'] / 1000:.0f} kHz")
    print(f"   Digital ports 1-2-3 contain  {len(Device['lines1'])} {len(Device['lines2'])} {len(Device['lines3'])} bits")
    
    # Clean up
    ai_task.close()
    ao_task.close()
    dio_task.close()
    
    return Device

# Example usage
# device_info = get_device_info()
# print(device_info)

def update_signal_values(negative_channel, positive_channel):
    # First 4 bits of wselect are stim1 location, last 4 bits are stim2 location.
    # Set initial nulcode: bits 4–7 high (16 + 32 + 64 + 128 = 240)
    encoded_flags = 0b11110000
    encoded_channels = 0

    if positive_channel > 1:
        encoded_channels += positive_channel
        encoded_flags -= 32  # clear bit 5

    if negative_channel > 1:
        encoded_channels += negative_channel * 16
        encoded_flags -= 64  # clear bit 6

    # Max value = 2^8 - 1 -> 255
    max_val = 255
    if encoded_flags > max_val:
        print("DIO error: port3 > 255. Did not write DIO, please report.")
        encoded_flags = 0

    # Turns on bit 8
    if encoded_flags < 128:
        encoded_flags += 128

    channel_vec = dec2binvec(encoded_channels, 8)
    flag_vec = dec2binvec(encoded_flags, 8)

    return channel_vec, flag_vec


def dec2binvec(value, length):
    # Convert decimal to binary vector of fixed length.
    return [int(bit) for bit in np.binary_repr(value, width=length)]


# def write_negative_signal(encoded_channels, encoded_flags):
#     value = round(Device['val3'])

#     max_val = 2 ** len(Device['lines3']) - 1
#     if value > max_val:
#         print("DIO error: port3 > 256. Did not write DIO, please report.")
#         value = 0

#     # Turns off bit 8
#     if value > 127:
#         value -= 128

#     combined_value = Device['val1'] + value * 256

#     bitvec = dec2binvec(combined_value, Device['len'])
#     putvalue(Device['lines'], bitvec)



def get_channels(deviceName, port_lists):
    negative_channel = 0
    positive_channel = 0
    input_channels = []

    for port in port_lists[0]:
        if port.startswith('A'):
            input_channels.append(deviceName + '/ai' + port[1:])
    
    for port in port_lists[1]:
        if port.startswith('M'):
            negative_channel = int(port[1:])
        elif port.startswith('P'):
            positive_channel = int(port[1:])

    print("Negative channel:", negative_channel)
    print("positive channel:", positive_channel)
    print("Input channels:", input_channels)
    return negative_channel, positive_channel, input_channels

def gaussian_filter(data):
    
    # Extract gauss width from UI (assuming it's a string of a number)
    gaussw = 0.001 * 250000 / 16

    if gaussw > 0:
        gauss = []
        total = 0
        width = 1

        # Build one-sided Gaussian until the relative contribution is < 1%
        while True:
            val = np.exp(-((width - 1) ** 2) / (2 * gaussw ** 2))
            gauss.append(val)
            total += val
            if (val / total) < 0.01:
                break
            width += 1

        # Build symmetric Gaussian kernel
        left = gauss[::-1][1:]
        right = gauss[1:]
        gauss_full = np.array(left + [1.0] + right)
        gauss_full /= np.sum(gauss_full)  # Normalize

        # Apply convolution to each column
        for col in range(data.shape[1]):
            data[:, col] = convolve(data[:, col], gauss_full, mode='same')

        return data

def generate_biphasic_waveform(duration, amplitude, sample_rate):
    num_samples = int(sample_rate * duration)
    half_samples = num_samples // 2
    waveform = np.concatenate([np.ones(half_samples), -np.ones(half_samples)]) * amplitude

    analog_data = np.zeros((num_samples, 2))
    analog_data[:, 0] = waveform
    analog_data[:, 1] = -waveform
    return analog_data, num_samples

def read_device(deviceName, portslists, max_voltage=1.5, sample_rate=50000, output_duration=2):
    system = System.local()
    for device in system.devices:
        print(f"\nDevice: {device.name}")
        print("Available Sample Clocks:")
        for terminal in device.terminals:
            if "SampleClock" in terminal:
                print(f"  - {terminal}")
    
    # Configure input and output channels
    negative_channel, positive_channel, input_channels = get_channels(deviceName, portslists)

    num_samples = int(sample_rate * output_duration)  # Total number of samples

    # Create a task for outputting voltage
    with nidaqmx.Task() as digital_output_task:
        channel_vec, flag_vec = update_signal_values(negative_channel, positive_channel)

        print(channel_vec)
        print(flag_vec)

        analog_waveform, ao_samples = generate_biphasic_waveform(output_duration, 1, sample_rate)

        # Configure output channels
        digital_output_task.do_channels.add_do_chan(deviceName + "/port0", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
        digital_output_task.do_channels.add_do_chan(deviceName + "/port2", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)

        # Create a task for reading input voltages
        with nidaqmx.Task() as input_task, nidaqmx.Task() as output_task:
            
            output_task.ao_channels.add_ao_voltage_chan(deviceName + "/ao0", min_val=-max_voltage, max_val=max_voltage)
            output_task.ao_channels.add_ao_voltage_chan(deviceName + "/ao1", min_val=-max_voltage, max_val=max_voltage)
            output_task.timing.cfg_samp_clk_timing(rate=sample_rate,
                                                   source="",
                                                   active_edge=nidaqmx.constants.Edge.RISING,
                                                   sample_mode=AcquisitionType.FINITE,
                                                   samps_per_chan=ao_samples)
            
            writer = AnalogMultiChannelWriter(output_task.out_stream, auto_start=False)
            writer.write_many_sample(analog_waveform.T.copy(order='C'))
        
            # Configure input channels
            for ch in input_channels:
                input_task.ai_channels.add_ai_voltage_chan(ch, min_val=0, max_val=5, units=VoltageUnits.VOLTS)

            # Configure timing for input task
            input_task.timing.cfg_samp_clk_timing(rate=sample_rate, 
                                                  source="/" + deviceName + "/ao/SampleClock",
                                                  active_edge=nidaqmx.constants.Edge.RISING,
                                                  sample_mode=AcquisitionType.FINITE, 
                                                  samps_per_chan=num_samples)
            
            # Create a reader for multiple channels
            reader = AnalogMultiChannelReader(input_task.in_stream)

            # Preallocate array for measured input
            input_voltage = np.zeros((len(input_channels), 100000))

            digital_output_task.start()
            # Write the output voltage values
            digital_output_task.write([channel_vec, flag_vec])

            input_task.start()
            output_task.start()

            output_task.wait_until_done(timeout=output_duration + 1)

            reader.read_many_sample(data=input_voltage, 
                                    number_of_samples_per_channel=100000, 
                                    timeout=output_duration + 1)
            
            input_task.wait_until_done()
            input_task.stop()
            output_task.stop()
        digital_output_task.stop()

        input_voltage = gaussian_filter(input_voltage)
    
    # Print the measured voltages from the input channels
    print(f"Measured voltages: {input_voltage}")
    
    return input_voltage