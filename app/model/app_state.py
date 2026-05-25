from dataclasses import dataclass

import pandas as pd

from app.model.config.stimulus_config import StimulusConfig


@dataclass(slots=True)
class AppState:
    stim_config: StimulusConfig
    experiment_config: dict
    experiment_metadata: dict
    raw_data_df: pd.DataFrame | None = None
    # filter_config: FilterConfig | None = None
