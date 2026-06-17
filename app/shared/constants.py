from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.filter.filter_config import FilterConfig
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig

# :)
APP_ORG = "UvA"
APP_TITLE = "Wormenpracticum"

# Margin and spacing for layouts
VIEW_MARGIN_DEFAULT = 20
VIEW_SPACING_DEFAULT = 18
LEFT_LAYOUT_STRETCH = 1
RIGHT_LAYOUT_STRETCH = 2

# Plot grid
PLOT_GRID_ALPHA_DEFAULT = 0.07
PLOT_PIN_SELECTED_PEN_WIDTH = 7
PLOT_PIN_UNSELECTED_PEN_WIDTH = 2

# View title labels
TITLE_LABEL_POINT_SIZE_INCREASE = 5

# Voltage limit for stimulus generation
DEFAULT_LIMIT_V = 1.5
DEFAULT_DUR_S = 0.01

# Segment parameter precision
DOUBLE_SPIN_NUM_DECIMALS = 4
DOUBLE_SPIN_PARSE_ROUND_DECIMALS = 7

# Resolution for pulse plot sampling
TARGET_N_SAMPLES_PULSE_PLOT = 9001

# Voltage and second magnitudes for pulse segment parameters
DOUBLE_SPIN_STEP_S = 0.0001
DOUBLE_SPIN_STEP_V = 0.1
DOUBLE_SPIN_MAX_S = 1.0
DOUBLE_SPIN_MAX_V = 2.0

# Segment highlighting
SEGMENT_VIEW_STIMULUS_HIGHLIGHT_DEFAULT = True


# Default configs moved from model.config
DEFAULT_PROTOCOL_CONFIG = ProtocolConfig(
    positive_channel=0,
    negative_channel=1,
    selected_pins=list(range(2, 17)),
    sample_rate_divider=1,
)

DEFAULT_FILTER_CONFIG = FilterConfig(
    low_pass_cutoff_hz=5000.0,
    suppress_50hz=True,
    remove_dc_offset=True,
)

DEFAULT_STIMULUS_CONFIG = StimulusConfig(
    dur_s=0.02,
    limit_v=1.5,
    n_steps=10,
    pulses=[
        Pulse(
            amp_v=1.5,
            start_s=0.001,
            step_start_s=0.0001,
            dur_s=0.0002,
        ),
        Pulse(
            amp_v=1.5,
            start_s=0.006,
            dur_s=0.0002,
        ),
    ],
)
