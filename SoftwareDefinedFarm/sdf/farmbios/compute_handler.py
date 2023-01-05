# System imports
from typing import Any


# Local packages
from sdf.farmbios.proto.compute_pb2 import ComputeRPC 
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.farmbios.base_handler import BaseRPCHandler


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS sensor RPC messages.
class ComputeRPCHandler(BaseRPCHandler):

    def __init__(self, module):
        super().__init__()
        self.module = module 


    def handle_message(self,
                       message: FarmBIOSMessage,
                       observer: Any = None,
                       callback_func: Any = None):
        """
           Process Compute RPC calls.
           :param message: The message pulled from the wire.
           :param observer: The local observer making the call.
           :param callback_func: The function to call with the results.
        """
        # Retrieve the call specs.
        rpc_info = message.compute
        metadata = rpc_info.procedure

        proc_type = metadata.WhichOneof("procedure_types")

        # The call back handling is internal to the application modules.
        if callback_func:
            return self.module.handle_callback(message, callback_func)

        if proc_type == "call":
            if metadata.call == CallType.ANALYTICS:
                self.log("COMPUTE: Call: ANALYTICS")
                # Execute the call according to any args specified
                resp_meta = ComputeRPC() 
                return self.module.analytics(message)
            elif metadata.call == CallType.RCV_SENSOR_NOTIFICATION:
                self.log("COMPUTE: Call: RCV SENSOR NOTIFICATION")
                return self.module.rcv_sensor_notification(message)
            elif metadata.call == CallType.RCV_STORAGE_NOTIFICATION:
                self.log("COMPUTE: Call: RCV STORAGE NOTIFICATION")
                return self.module.rcv_storage_notification(message)
            else:
                self.log("Unknown compute RPC %s. Ignoring" % metadata.call)
        elif proc_type == "response":
            if metadata.response == ResponseType.SUCCESS:
                self.log("COMPUTE: Response: SUCCESS")
                return self.module.handle_callback(message)
            elif metadata.response == ResponseType.ERROR:
                self.log("COMPUTE: Response: ERROR")
                # TODO: Handle the erroneous results
            else:
                self.log("Unknown compute result %s\n" % \
                         metadata.response)
        else:
            self.log("Unknown procedure type, ignoring")

        # Return nothing to the dispatcher in any other case
        return None, None
