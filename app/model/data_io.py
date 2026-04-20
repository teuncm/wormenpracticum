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
