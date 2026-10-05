import json

import pandas as pd


def write_data(file_path, df) -> None | str:
    """Write experiment data to a CSV file.

    Args:
        file_path (str): The path to the CSV file to write.
        df (pd.DataFrame): The DataFrame to write to the CSV file.

    Returns:
        None | str: None if successful, or an error message if an error occurs.
    """
    try:
        df.to_csv(file_path, index=False, float_format="%.9g")
    except Exception as e:
        return str(e)


def read_data(file_path) -> pd.DataFrame | str:
    """Read experiment data in CSV format from file path.

    Args:
        file_path (str): The path to the CSV file to read.

    Returns:
        pd.DataFrame | str: The DataFrame read from the CSV file, or an error message if an error occurs.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        return str(e)


def write_metadata(file_path, metadata) -> None | str:
    """Write experiment metadata to a JSON file.

    Args:
        file_path (str): The path to the JSON file to write.
        metadata (dict): The metadata dictionary to write to the JSON file.

    Returns:
        None | str: None if successful, or an error message if an error occurs.
    """
    try:
        with open(file_path, "w") as f:
            json.dump(metadata, f, indent=4)
    except Exception as e:
        return str(e)


def read_metadata(file_path) -> dict | str:
    """Read metadata from a JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        return str(e)


def read_recording_metadata(file_path) -> tuple[dict, dict] | str:
    """Read the existing recording JSON wrapper into metadata and saved settings."""
    state = read_metadata(file_path)
    if isinstance(state, str):
        return state
    if (
        not isinstance(state, dict)
        or "metadata" not in state
        or any(
            not isinstance(state.get(key, {}), dict)
            for key in ("metadata", "experiment_config", "stim_config")
        )
    ):
        return "Invalid recording format."
    config = dict(state.get("experiment_config", {}))
    if "stim_config" in state:
        config["stim_config"] = state["stim_config"]
    return state["metadata"], config
