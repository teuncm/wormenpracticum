from pathlib import Path

import app.model.stimulus.signal as sgn
import numpy as np
import pandas as pd
from app.model.data_io import (
    write_data,
)


def gen_dummy_data(
    t_max, sample_rate, num_i_chan, num_o_chan, num_stims, num_reps=1
) -> pd.DataFrame:
    """Generate matrix with 16 sine waves for testing."""
    # Total number of samples
    N = sgn.quantize_time_point(time_s=t_max, sr_hz=sample_rate)
    timestamps = np.round(np.linspace(0, t_max, num=N, endpoint=False), 5)

    print(timestamps)

    t = pd.Series(timestamps, name="t_(s)")

    stim_list = []
    for i in range(num_stims):
        for j in range(num_i_chan):
            signal = 0 * timestamps
            stim_list.append(pd.Series(signal, name=f"s{i}_i{j}_(V)"))

        for j in range(num_o_chan):
            for k in range(num_reps):
                signal = 0 * timestamps
                stim_list.append(pd.Series(signal, name=f"s{i}_o{j}_r{k}_(V)"))

    df = pd.concat([t, *stim_list], axis=1)

    return df


def main():
    dummy_df = gen_dummy_data(
        t_max=0.0010,
        sample_rate=10000,
        num_i_chan=3,
        num_o_chan=2,
        num_stims=3,
        num_reps=3,
    )

    file_path = Path("data/test_data.csv")
    if file_path:
        write_data(file_path, dummy_df)


if __name__ == "__main__":
    main()
