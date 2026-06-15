from app.feature.acquisition.protocol_mapping import (
    encode_stim_channel_pair,
    get_logical_channel_labels,
    get_logical_measurement_channel_labels,
    get_logical_stim_channel_labels,
)


def test_get_logical_channel_labels():
    """Verify that the shared logical labels match the MATLAB UI."""
    expected_labels = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
    ]

    assert get_logical_channel_labels() == expected_labels
    assert get_logical_stim_channel_labels() == expected_labels
    assert get_logical_measurement_channel_labels() == expected_labels


def test_encode_stim_channel_pair_matches_matlab_default():
    """Verify the reverse-engineered MATLAB default selection encoding."""
    assert encode_stim_channel_pair(1, 2) == {"port1": 16, "port3": 176}


def test_encode_stim_channel_pair_matches_matlab_non_default():
    """Verify a non-default logical channel pair against the MATLAB formula."""
    assert encode_stim_channel_pair(5, 9) == {"port1": 132, "port3": 144}
