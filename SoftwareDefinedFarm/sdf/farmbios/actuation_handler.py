# System imports
from typing import Any


# Local packages
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import CallType
from sdf.farmbios.base_handler import BaseRPCHandler


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS actuation RPC messages.
class ActuationRPCHandler(BaseRPCHandler):

    def __init__(self, module):
        super().__init__()
        self.module = module 


    def handle_message(self,
                       message: FarmBIOSMessage,
                       observer: Any = None,
                       callback_func: Any = None):
        """
           Process Actuation RPC calls.
           :param message: The message pulled from the wire.
           :param observer: The local observer making the call.
           :param callback_func: The function to call with the results.
        """
        # Retrieve the call specs.
        rpc_info = message.actuation
        metadata = rpc_info.procedure

        proc_type = metadata.WhichOneof("procedure_types")

        # The call back handling is internal to the application modules.
        if callback_func:
            return self.module.handle_callback(message, callback_func)

        if proc_type == "call":
            if metadata.call == CallType.ACTIVATE:
                self.log("ACTUATION: Call: ACTIVATE")
                return self.module.activate(message)
            else:
                self.log("Unknown compute RPC %s. Ignoring" % metadata.call)
