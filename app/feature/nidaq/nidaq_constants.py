# Base status values for NI-DAQ devices.
NI_DAQ_UNAVAILABLE_STATUS = "NI-DAQ device not found"

# Base rate for synchronized stimulation and acquisition, before protocol division.
NI_DAQ_BASE_SAMPLE_RATE_HZ = 15600

# Polling interval for refreshing NI-DAQ discovery status in the UI (in milliseconds).
# Allows us to get rid of the connect/disconnect buttons.
NI_DAQ_DISCOVERY_POLL_INTERVAL_MS = 1000
