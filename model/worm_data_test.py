import sys

import numpy as np
import pandas as pd
from data_functions import (
    load_data,
    save_data,
    show_load_dialog,
    show_save_dialog,
)
from PySide6.QtWidgets import QApplication


def gen_dummy_data(t_max=10e6, N=1000) -> pd.DataFrame:
    """Generate matrix with 16 sine waves for testing."""
    timestamps = np.linspace(0, t_max, num=N)

    data = np.array(
        [timestamps]
        + [np.sin(2 * np.pi * f * timestamps / t_max) for f in range(1, 17)]
    ).T

    df = pd.DataFrame(
        data, columns=["Timestamp (ms)"] + [f"Channel {i} (uV)" for i in range(1, 17)]
    )

    return df


def main():
    _ = QApplication(sys.argv)

    dummy_df = gen_dummy_data(t_max=10e6, N=50000000)

    print(dummy_df)

    file_path = show_save_dialog()
    if file_path:
        save_data(file_path, dummy_df)

    file_path2 = show_load_dialog()

    if file_path2:
        loaded_df = load_data(file_path2)
        print(loaded_df)


if __name__ == "__main__":
    main()
