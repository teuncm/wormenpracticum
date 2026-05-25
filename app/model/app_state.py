from dataclasses import dataclass

import pandas as pd

from app.model.config.filter_config import FilterConfig
from app.model.config.protocol_config import ProtocolConfig
from app.model.config.stimulus_config import StimulusConfig


@dataclass(slots=True)
class AppState:
    stim_config: StimulusConfig
    protocol_config: ProtocolConfig
    filter_config: FilterConfig
    experiment_config: dict
    experiment_metadata: dict
    raw_data_df: pd.DataFrame | None = None
