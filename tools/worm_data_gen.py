from pathlib import Path

import numpy as np
import pandas as pd
from app.model.data_io import (
    write_data,
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
    dummy_df = gen_dummy_data(t_max=0.0010, sample_rate=100000, num_channels=2)

    print(dummy_df)

    file_path = Path("data/test_data.parquet")
    if file_path:
        write_data(file_path, dummy_df)


if __name__ == "__main__":
    main()
