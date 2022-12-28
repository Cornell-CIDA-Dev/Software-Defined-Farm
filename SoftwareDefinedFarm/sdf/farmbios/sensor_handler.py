# System imports
from typing import Any


# Local packages
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import ResponseType, CallType


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS sensor messages.
class SensorRPCHandler(BaseRPCHandler):

    def __init__(self, module):
        super().__init__()
        self.module = module 


    def handle_message(self,
                       message: FarmBIOSMessage,
                       observer: Any = None,
                       callback_func: Any = None,
                       **kwargs):
        """
           Process Sensor RPC calls.
           :param message: The message pulled from the wire.
           :param observer: The local observer making the call.
           :param callback_func: The function to call with the results.
        """
        # Retrieve the call specs.
        rpc_info = message.sensor
        metadata = rpc_info.procedure

        # The call back handling is internal to the application modules.
        if callback_func:
            return self.module.handle_callback(message, callback_func)

        proc_type = metadata.WhichOneof("procedure_types")
        if proc_type == "call":
            if metadata.call == CallType.REGISTER:
                self.log("SENSOR: Call: REGISTER\n")
                return self.module.register(message, observer) 
            # For other modules to receive remote sensor notifications.
            elif metadata.call == CallType.NOTIFY:
                self.log("SENSOR: Call: NOTIFY\n")
                if observer != None:
                    observer.rcv_sensor_notification(data)
                return None
            elif metadata.call == CallType.READ:
                self.log("SENSOR: Call: READ\n")
                return self.module.read(message)
        if proc_type == "response":
            if metadata.response == ResponseType.REGISTER_SUCCESS:
                self.log("SENSOR: Response: REGISTER_SUCCESS\n")
                # Process register success
                return None
            if metadata.response == ResponseType.REQUESTED_DATA:
                self.log("SENSOR: Response: REQUESTED_DATA\n")
                # Process requested data
                return None
