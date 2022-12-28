# System imports
from time import time
from typing import Optional, Any, Union
from uuid import uuid4


# Local packages
from sdf.helper_typedefs import CallBackRecord
from sdf.farmbios.proto.actuation_pb2 import ActuationRPC 
from sdf.farmbios.proto.compute_pb2 import ComputeRPC 
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage 
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.storage_pb2 import StorageRPC 
from sdf.helper_typedefs import Modules as mod

# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


def get_farmbios_message(msg_type: mod,
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


def get_callback_record(return_addr: Any,
                        request_dispatch: str,
                        register_module: str,
                        callback_func: Any,
                       ):
    """
       Create a callback record to be tied to an outgoing message.
       :param return_addr: The peer that will be contacted after 
                           processing the results from the call back.
       :param request_dispatch: The module that will receive the outgoing message..
       :param register_module: The module that will process the returning
                               results. 
       :param callback_func: The function to call with the results.
    """ 
    callback_record = CallBackRecord(eventual_return_addr=return_addr,
                                     request_dispatch=request_dispatch,
                                     register_module=register_module,
                                     registration_ts=str(time()),
                                     next_call=callback_func,
                                     identifier=str(uuid4())
                             )
    print("%s callback will be: %s\n" % (callback_func.name,
                                         callback_record.identifier))
    return callback_record
