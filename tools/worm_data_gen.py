from pathlib import Path

import app.model.stimulus.signal as sgn
import numpy as np
import pandas as pd
from app.model.data_io import (
    write_data,
)


def gen_dummy_data(t_max, sample_rate, num_stims, num_resps) -> pd.DataFrame:
    """Generate matrix with 16 sine waves for testing."""
    # Total number of samples
    N = sgn.quantize_time_point(time_s=t_max, sr_hz=sample_rate)
    timestamps = np.linspace(0, t_max, num=N, endpoint=False)

    stims = np.array([(0 * timestamps) for _ in range(num_stims)])
    resps = np.array([(0 * timestamps) for _ in range(num_resps)])

    # stims += np.random.normal(scale=0.1, size=waves.shape)

    data = np.array(
        [timestamps]
        + [stims[i] for i in range(num_stims)]
        + [resps[i] for i in range(num_resps)]
    ).T

    df = pd.DataFrame(
        data,
        columns=["Timestamp (s)"]
        + [f"Channel {i} (V)" for i in range(num_stims + num_resps)],
    )

    return df


def main():
    dummy_df = gen_dummy_data(
        t_max=0.0010, sample_rate=100000, num_stims=1, num_resps=1
    )

    print(dummy_df)

    file_path = Path("data/test_data.parquet")
    if file_path:
        write_data(file_path, dummy_df)


if __name__ == "__main__":
    main()
