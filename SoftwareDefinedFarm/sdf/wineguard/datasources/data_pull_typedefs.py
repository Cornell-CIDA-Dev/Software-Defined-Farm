from enum import Enum
from collections import namedtuple


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: Definitions for request types to be made to NASA EarthCloud
class TaskTypes(Enum):
    AREA = "area"
    POINT = "point"


# @brief: Definitions for spatial projection types
class SpatialProjections(Enum):
    NATIVE = "native"
    GEOGRAPHIC = "geographic"
    MODIS_SINUSOIDAL = "sinu_modis"


# @brief: Definitions for output format types
class OutputTypes(Enum):
    GEOTIFF = "geotiff"
    NETCDF4 = "netcdf4"


# Definitions for module raw strings
# This allows for cleaner development by using enums
#class Modules(Enum):
#    SENSOR = "sensor"
#    STORAGE = "storage"
#    COMPUTE = "compute"
#    ACTUATION = "actuation"
#    CONFIG = "config"
