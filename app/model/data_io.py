import pandas as pd


def write_data(file_path, df) -> None:
    """Write experiment data to a Parquet file.

    Args:
        file_path (str): The path to the Parquet file to write.
        df (pd.DataFrame): The DataFrame to write to the Parquet file.
    """
    df.to_parquet(file_path, index=False)


def read_data(file_path) -> pd.DataFrame:
    """Read experiment data in Parquet format from file path

    Args:
        file_path (str): The path to the Parquet file to read.

    Returns:
        pd.DataFrame: The DataFrame read from the Parquet file.
    """
    return pd.read_parquet(file_path)
