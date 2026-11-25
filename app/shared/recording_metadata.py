"""Validation for the sample layout and pin mapping saved with a recording."""

from math import isfinite


def validate_sample_rate(value: object) -> float:
    """Return a positive finite clock rate in Hz."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            if isfinite(value) and value > 0:
                return float(value)
        except OverflowError:
            pass
    raise ValueError("Recorded sample rate must be positive and finite.")


def _pin_number(value: object) -> int | None:
    if type(value) is int:
        return value if value > 0 else None
    # Older pin maps can store an integral pin number as a float or string.
    if isinstance(value, (float, str)):
        try:
            number = float(value)
        except ValueError:
            return None
        if number >= 1 and number.is_integer():
            return int(number)
    return None


def recording_pin_channels(metadata: dict) -> dict[str, int]:
    """Return valid pin labels, leaving unmapped channels to the caller."""
    mapping = metadata.get("pin_channels")
    if not isinstance(mapping, dict):
        return {}
    return {
        column: pin
        for column, value in mapping.items()
        if isinstance(column, str) and column and column != "t_(s)"
        if (pin := _pin_number(value)) is not None
    }


def _validate_sample_layout(metadata: dict, row_count: int | None) -> None:
    if "sample_rate_hz" in metadata:
        validate_sample_rate(metadata["sample_rate_hz"])

    for key, minimum in (
        ("stimulus_size_samples", 1),
        ("stimulus_count", 1),
        ("sample_count", 0),
    ):
        if key in metadata and (
            type(metadata[key]) is not int or metadata[key] < minimum
        ):
            raise ValueError(f"Invalid recorded {key.replace('_', ' ')}.")

    sample_count = metadata.get("sample_count", row_count)
    if row_count is not None and sample_count != row_count:
        raise ValueError("Sample count does not match the loaded recording.")

    size = metadata.get("stimulus_size_samples")
    count = metadata.get("stimulus_count")
    if (
        size is not None
        and count is not None
        and sample_count is not None
        and size * count != sample_count
    ):
        raise ValueError("Recorded samples do not match the stimulus boundaries.")


def validate_recording_metadata(metadata: dict, row_count: int | None = None) -> None:
    """Validate supplied fields without requiring metadata for a bare recording."""
    _validate_sample_layout(metadata, row_count)
    if "pin_channels" in metadata:
        mapping = metadata["pin_channels"]
        if not isinstance(mapping, dict) or len(
            recording_pin_channels(metadata)
        ) != len(mapping):
            raise ValueError(
                "Recorded pin channels must map voltage columns to positive pin numbers."
            )


def stimulus_layout(metadata: dict, row_count: int) -> tuple[int, int, float]:
    """Return the size, count, and clock rate required to split a recording."""
    _validate_sample_layout(metadata, row_count)
    if "stimulus_size_samples" not in metadata or "stimulus_count" not in metadata:
        raise ValueError("Stimulus size and count are required.")
    if "sample_rate_hz" not in metadata:
        raise ValueError("Recorded sample rate is required.")
    return (
        metadata["stimulus_size_samples"],
        metadata["stimulus_count"],
        metadata["sample_rate_hz"],
    )


def build_recording_metadata(
    device_name: str,
    sample_rate_hz: float,
    stimulus_size_samples: int,
    stimulus_count: int,
    sample_count: int,
) -> dict:
    """Build metadata for the standard 16-channel recording layout."""
    metadata = {
        "device_name": device_name,
        "sample_rate_hz": sample_rate_hz,
        "stimulus_size_samples": stimulus_size_samples,
        "stimulus_count": stimulus_count,
        "sample_count": sample_count,
        # Keep the existing CSV names and one-based physical pin numbers.
        "pin_channels": {f"ai{index}_(V)": index + 1 for index in range(16)},
    }
    validate_recording_metadata(metadata)
    return metadata
