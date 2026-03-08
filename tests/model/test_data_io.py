from pathlib import Path

import pandas as pd
from app.model.data_io import read_data, write_data


def test_save_load_data(tmp_path):
    """Verify that loaded data equals saved data using the data I/O functions."""
    test_df = pd.DataFrame(
        {"Timestamp (s)": [0.0, 0.001, 0.002], "Channel 1 (V)": [0.1, 0.2, 0.3]}
    )

    file_path = Path(tmp_path) / "test_data.parquet"

    write_data(file_path, test_df)
    loaded_df = read_data(file_path)

    assert test_df.equals(loaded_df)
