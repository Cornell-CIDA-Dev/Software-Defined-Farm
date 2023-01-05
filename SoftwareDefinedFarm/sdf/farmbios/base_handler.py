# System imports
from typing import Any, Optional, Union, TypeVar
from abc import abstractmethod


# Local packages
from sdf.farmbios.proto.actuation_pb2 import ActuationRPC 
from sdf.farmbios.proto.compute_pb2 import ComputeRPC 
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage 
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.storage_pb2 import StorageRPC 
from sdf.helper_typedefs import Modules as mod
from sdf.utils.universal_base_class import UniversalBase


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# Stand-in type definition for RPC types
Message = TypeVar('Message')


# @brief: The base handler of FarmBIOS RPCs.
class BaseRPCHandler(UniversalBase):


    def __init__(self):
        super().__init__()


    @abstractmethod
    def handle_message(self,
                       message: Message,
                       **kwargs):
        """
           Handle a message originating from the wire.
        """


    def get_farmbios_message(self,
                             msg_type: mod,
                             metadata: Union[SensorRPC,
                                             StorageRPC,
                                             ComputeRPC,
                                             ActuationRPC],
                             data: Optional[Any] = None,
                             callback_id: Optional[str] = None,
                             is_final_response: Optional[bool] = None):
        """
           Package a farmbios message for sending over the wire.
           :param msg_type: The type of module RPC call being made.
           :param metadata: The RPC metadata to be used by the dispatcher.
           :param data: Any data to be added and introspected by the peer.
           :param callback_id: The identifier for a callback.
           :param is_final_response: The distinguisher between callback responses. 
        """
    
        message = FarmBIOSMessage()
        if msg_type == mod.SENSOR:
            message.sensor.CopyFrom(metadata) 
        elif msg_type == mod.STORAGE:
            message.storage.CopyFrom(metadata) 
        elif msg_type == mod.COMPUTE:
            message.compute.CopyFrom(metadata) 
        elif msg_type == mod.ACTUATION:
            message.actuation.CopyFrom(metadata) 
    
        if data:
            message.data = data
    
        if callback_id != None:
            message.callback.identifier = callback_id
    
        if is_final_response == True:
            message.callback.isFinalResponse = True
    
        return message 


    def get_callback_tuple(self, callback_func: Any):
        """
           Create a callback to be tied to an outgoing message.
           :param callback_func: The function to call with the results.
        """ 
        callback = CallBackRecord(eventual_return_addr=None,
                                  request_dispatch="storage",
                                  register_module="sensor",
                                  registration_ts=str(time()),
                                  next_call=callback_func
                                 )
        callback_id = str(uuid4())
        self.log("%s callback will be: %s\n" % (callback_func.name,
                                                callback_id))
        return tuple([callback_id, callback])
