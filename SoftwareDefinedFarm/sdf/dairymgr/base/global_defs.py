from enum import Enum
from math import pow
from collections import namedtuple
from dataclasses import dataclass


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: An enum class for passing casting arguments in processors.
class Casts(Enum):
    INT = 1
    STR = 2
    FLOAT = 3
    SINT = 4
    BOOL = 5
    NO_CAST = 6


# @brief: An enum class for major dairy management systems
class Providers(Enum):
    VENDOR_ONE = 1
    VENDOR_TWO = 2
    VENDOR_THREE = 3   


# @brief: A class definition for mutably mapping sensors to their status info.
@dataclass
class SensorInfo:
    name: str
    directory: str
    latest_ts: float

# @brief: A type definition for mapping sensor names to their modules
ModuleMapper = namedtuple('ModuleMapper', ['name', 'module'])

# @brief: A type definition mapping sensor updates and when/where they occur.
SensorUpdate = namedtuple('SensorUpdate',
                          ['sensor_name', 'file_name', 'timestamp'])

# Define globals for sensor information
ZERO_TS = 0.0


# Define globals for limits on protobuf message sizes.
FLOOR_MSG_SIZE = pow(2, 13) 
CEILING_MSG_SIZE = pow(2, 14)
ROW_COUNTER = 200
VENDOR_ONE_ROW_COUNTER = 20

# Define globals for periodic and snapshot checks.

# The periodic check in minutes
SIXTY_SECONDS = 60

# The snapshot interval in seconds.
SNAPSHOT_INTERVAL = 10

# Define globals for networking operations
ZERO_BYTES = 0
SOCKET_TIMEOUT = 20
MESSAGE_SIZE = 3
BYTE_LIMIT = 4096
ALL_INTERFACES = '0.0.0.0'

# Wait interval to ensure peer server doesn't get overwhelmed.
THROTTLE_INTERVAL = 2
MAX_QUEUE_SIZE = 3
