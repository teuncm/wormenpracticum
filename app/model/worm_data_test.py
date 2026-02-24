import sys

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication

from app.model.data_functions import (
    load_data,
    save_data,
    show_load_dialog,
    show_save_dialog,
)


def gen_dummy_data(t_max, sample_rate, num_channels) -> pd.DataFrame:
    """Generate matrix with 16 sine waves for testing."""
    # Wave frequency in Hz
    WAVE_FREQ = 10000
    # Total number of samples
    N = int(t_max * sample_rate)
    # Samples are measured in milliseconds
    timestamps = np.linspace(0, t_max, num=N, endpoint=False)

    waves = np.array(
        [np.sin(2 * np.pi * WAVE_FREQ * timestamps) for _ in range(num_channels)]
    )

    waves += np.random.normal(scale=0.1, size=waves.shape)

    data = np.array([timestamps] + [waves[i] for i in range(num_channels)]).T

    df = pd.DataFrame(
        data,
        columns=["Timestamp (s)"] + [f"Channel {i} (V)" for i in range(num_channels)],
    )

    return df


def main():
    _ = QApplication(sys.argv)

    dummy_df = gen_dummy_data(t_max=0.0010, sample_rate=100000, num_channels=2)

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
