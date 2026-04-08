from pathlib import Path

import app.model.stimulus.signal as sgn
import numpy as np
import pandas as pd
from app.model.data_io import (
    write_data,
)


def gen_dummy_data(
    t_max, sample_rate, num_i_chan, num_o_chan, num_stims
) -> pd.DataFrame:
    """Generate matrix with 16 sine waves for testing."""
    # Total number of samples
    N = sgn.quantize_time_point(time_s=t_max, sr_hz=sample_rate)
    timestamps = np.linspace(0, t_max, num=N, endpoint=False)

    t = pd.Series(timestamps, name="t (s)")

    stim_list = []
    for i in range(num_stims):
        for j in range(num_i_chan):
            signal = 0 * timestamps
            stim_list.append(pd.Series(signal, name=f"s{i}_i{j} (V)"))

        for j in range(num_o_chan):
            signal = 0 * timestamps
            stim_list.append(pd.Series(signal, name=f"s{i}_o{j} (V)"))

    df = pd.concat([t, *stim_list], axis=1)

    return df


def main():
    dummy_df = gen_dummy_data(
        t_max=0.0010, sample_rate=10000, num_i_chan=2, num_o_chan=2, num_stims=3
    )

    file_path = Path("data/test_data.parquet")
    if file_path:
        write_data(file_path, dummy_df)


if __name__ == "__main__":
    main()
