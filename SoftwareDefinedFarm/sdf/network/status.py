from enum import Enum


# @brief: an enumeration of receiving failures.
class CommunicationStatus(Enum):
    SOCKET_ERROR = 1
    SUCCESS = 2
    NO_DATA = 3
    NETWORK_OUTAGE = 4

# Define globals for networking operations
ZERO_BYTES = 0
SOCKET_TIMEOUT = 20
MESSAGE_SIZE = 3
BYTE_LIMIT = 4096
ALL_INTERFACES = '0.0.0.0'
