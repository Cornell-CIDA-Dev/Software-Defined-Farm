# System imports
from typing import Any


# Local packages
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS sensor messages.
class ConfigRPCHandler(BaseRPCHandler):

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
        # The call back handling is internal to the application modules.
        if callback_func:
            return self.module.handle_callback(message, callback_func)
        else:
            self.log("Unexpected call to Config handler. Ignoring\n")
        return None, None
