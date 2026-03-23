# Base status values for NI-DAQ devices.
NI_DAQ_UNAVAILABLE_STATUS = "NI-DAQ unavailable"
NI_DAQ_NOT_READY_STATUS = NI_DAQ_UNAVAILABLE_STATUS
NI_DAQ_NOT_DISCOVERED_STATUS = NI_DAQ_UNAVAILABLE_STATUS
NI_DAQ_DISCONNECTED_STATUS = NI_DAQ_UNAVAILABLE_STATUS

# Polling interval for refreshing NI-DAQ discovery status in the UI (in milliseconds).
# Allows us to get rid of the connect/disconnect buttons.
NI_DAQ_DISCOVERY_POLL_INTERVAL_MS = 1000
