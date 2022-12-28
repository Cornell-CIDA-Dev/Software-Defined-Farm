from enum import Enum

from sdf.farmbios.proto.shared_pb2 import CallType as shared_ctypes
from sdf.waterguard.proto.waterguard_pb2 import (WaterGuardConfigCallBacks as watg_conf_cb,
                                                WaterGuardSensorCallBacks as watg_sens_cb,
                                                WaterGuardComputeCallBacks as watg_comp_cb)

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class WaterGuardConfigCallBacks(Enum):
   FINISH_SENSORBOX_CONFIG = watg_conf_cb.FINISH_SENSORBOX_CONFIG 
   PROCESS_WATCHTABLE_PRESENCE = watg_conf_cb.PROCESS_WATCHTABLE_PRESENCE 
   INSERT_LATEST_ROWKEY = watg_conf_cb.INSERT_LATEST_ROWKEY 


class WaterGuardSensorCallBacks(Enum):
    SET_TOP_ROW_KEY = watg_sens_cb.SET_TOP_ROW_KEY 
    QUERY_NEW_ROWKEYS = watg_sens_cb.QUERY_NEW_ROWKEYS 
    PROCESS_READ_RESULTS = watg_sens_cb.PROCESS_READ_RESULTS 


class WaterGuardComputeCallBacks(Enum):
    CONFIRM_REGISTRATION = watg_comp_cb.CONFIRM_REGISTRATION 
    ANALYTICS = shared_ctypes.ANALYTICS 
