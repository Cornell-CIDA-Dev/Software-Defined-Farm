from enum import Enum

from sdf.dairymgr.proto.dairymgr_pb2 import (DairyMgrComputeCallBacks as \
                                             dmgr_compute_cb)

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class DairyMgrComputeCallBacks(Enum):
    CONFIRM_REGISTRATION = dmgr_compute_cb.CONFIRM_REGISTRATION 
    PROCESS_READ_DATA = dmgr_compute_cb.PROCESS_READ_DATA
