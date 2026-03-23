"""Logical channel mapping used by the protocol editor.

The MATLAB app exposed the same 01..16 logical labels for both stimulation
selection and measurement display, even though the underlying NI-DAQ hardware
uses a separate physical pin layout.
"""

LOGICAL_CHANNEL_COUNT = 16


def get_logical_channel_labels():
    return [f"{channel:02d}" for channel in range(1, LOGICAL_CHANNEL_COUNT + 1)]


def get_logical_stim_channel_labels():
    return get_logical_channel_labels()


def get_logical_measurement_channel_labels():
    return get_logical_channel_labels()


def encode_stim_channel_pair(positive_channel: int, negative_channel: int) -> dict[str, int]:
    """Encode the logical 1..16 stim selections the way the MATLAB app did.

    The original MATLAB code packed the two selected channels into a byte for
    port 1 and used a fixed upper-nibble pattern on port 3 to gate the output.
    """
    if not 1 <= positive_channel <= LOGICAL_CHANNEL_COUNT:
        raise ValueError("positive_channel must be between 1 and 16")
    if not 1 <= negative_channel <= LOGICAL_CHANNEL_COUNT:
        raise ValueError("negative_channel must be between 1 and 16")

    port1_value = 0
    port3_value = 16 + 32 + 64 + 128

    if positive_channel > 1:
        port1_value += positive_channel - 1
        port3_value -= 32

    if negative_channel > 1:
        port1_value += (negative_channel - 1) * 16
        port3_value -= 64

    return {
        "port1": round(port1_value),
        "port3": round(port3_value),
    }
