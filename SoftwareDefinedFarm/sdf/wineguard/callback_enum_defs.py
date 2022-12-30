# System imports
from enum import Enum


# Local imports
from sdf.wineguard.proto.wineguard_pb2 import (ComputeCallBacks as compute_cb)


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class WineGuardComputeCallBacks(Enum):
    PROCESS_RESULTS = compute_cb.PROCESS_RESULTS 
