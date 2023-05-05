# System imports
from socket import socket
from typing import Any, List, Dict, Union, Tuple


# Local packages
from sdf.config.base_config import BaseConfig
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.helpers import get_farmbios_message, get_callback_record
from sdf.farmbios.proto.compute_pb2 import ComputeRPC 
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage 
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.storage_pb2 import StorageRPC 
from sdf.farmbios.proto.shared_pb2 import ResponseType
from sdf.helper_typedefs import CallBackRecord, Modules as mod, OutgoingMessage
from sdf.network.network_manager import NetworkManager
from sdf.network.status import CommunicationStatus as comstatus
from sdf.sensors.base_sensor import SensorModule
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase 


# Third party packages
from google.protobuf.internal.encoder import _VarintBytes


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The dispatch of FarmBIOS messages.
class Dispatcher(ThreadedUniversalBase):

    def __init__(self,
                 handlers: Dict[str, BaseRPCHandler],
                 config: BaseConfig,
                 **kwargs):
        """
           Initialize the dispatch with access to network management.
           :param handlers: The classes to call upon receiving a message.
           :param config: The application configuration.
        """
        super().__init__()
        self.handlers = handlers
        self.config = config
        self.call_backs = {}
        self.handler_mapping = {"sensor": mod.SENSOR,
                                "storage": mod.STORAGE,
                                "compute": mod.COMPUTE,
                                "actuation": mod.ACTUATION
                                }
        self.exit_signal = False


    def set_network_manager(self,
                            net_mgr: NetworkManager):
        """
           Set the network manager to be used locally.
           :param net_mgr: The connection and message queue handler.
        """
        self.net_mgr = net_mgr


    def unregister(self,
                   peer: Any = None,
                   all_conns: bool = False):
        """
            Remove any connections that may have registered with the
            handlers' modules. This is most applicable to the sensor
            module because it is the only module that makes register calls.
            This can also be used in the future if we support an
            unregister call.
            :param peer: The observer to remove as registrant.
            :param all_conns: Determines if all connections should be removed.
        """
        for sensor_type, handler in self.handlers.items():
            module_type = type(handler.module)
            is_sensor_module = issubclass(module_type, SensorModule)
            if is_sensor_module and not(all_conns):
                handler.module.remove_registrations(peer=peer)
                break
            elif is_sensor_module and (all_conns == True):
                handler.module.remove_registrations()
                break

    def update_connection_pointer(self,
                                  destination: mod,
                                  new_conn: socket
                                  ):
        """
           Update the connection pointer for easier processing next time.
           :param destination: The recepient module.
           :param new_conn: The connection to be associated a remote module.
        """
        if destination == mod.SENSOR:
            self.config.sensor_conn = new_conn
        elif destination == mod.STORAGE:
            self.config.storage_conn = new_conn
        elif destination == mod.COMPUTE:
            self.config.compute_conn = new_conn
        elif destination == mod.ACTUATION:
            self.config.actuation_conn = new_conn


    def route_message(self,
                      destination: mod,
                      connection: Union[socket, BaseRPCHandler, None],
                      peer_address: Tuple[str, int],
                      message_list: List[FarmBIOSMessage]):
        """
           Find the appropriate route for outgoing messages.
           :param destination: The recepient module.
           :param connection: The peer connection/handler (if any)
           :param peer_address: The IP,Port on which to retry connections.
           :param message_list: The messages to be sent.
        """
        # The common case
        if type(connection) == socket:
           self.log("Routing to existing conn %s\n" % connection) 
           self.send_messages(message_list, connection)
        # The less common case, i.e. the connection is actually a local handler
        elif issubclass(type(connection), BaseRPCHandler):
            self.send_messages(message_list, connection)
        # The unlikely case, i.e. the connection was not set on a previous try
        elif connection == None:
            status, connection = self.config.get_or_set_peer_conn(peer_address)
            if status == comstatus.SUCCESS:
                self.send_messages(message_list, connection)
                self.update_connection_pointer(destination, connection)
            else:
                self.log("No connection to %s module." % destination.name)
                self.log("Reconnect attempt returned %s\n" % status)
                self.log("Skipping send for current message list.\n")
        # The very unlikely case, i.e. the connection type is unknown
        else: # Very unlikely
            self.log("Unknown type ( %s ) for %s connection \n" % \
                                           ( type(connection), destination) )
            self.log("Skipping send for current message list.\n")


    def compose_outbound(self,
                         metadata: Any,
                         composer: mod,
                         destination: mod,
                         callback_func: Any,
                         register_callback: bool = True,
                         return_addr: Any = None,
                        ):
        """
           Compose an outgoing message (including callback if needed).
           We created this method because the same code seems to be repeated
           in a lot of the modules, and it takes a lot of development effort
           to update it.
           :param metadata: The metadata specifying if it is a sensor,
                            compute, storage, or actuation message.
           :param composer: The module composing said message.
           :param destination: The recepient module.
           :param register_callback: A boolean indicating whether a callback
                                     record should be created for the message.
           :param return_addr: If callback registration is true, indicating
                               the ultimate receiver of the returned results
                               where the composer is serving as a middleman.
                               We may end up removing this field..
           :param callback_func: If callback registration is true, this field
                                 will be set appropriately by the composer.
        """
        callback_record = get_callback_record(return_addr=return_addr,
                                              request_dispatch=destination,
                                              register_module=composer,
                                              callback_func=callback_func)

        # Get a FarmBIOS message and set the callback id
        farmbios_msg = get_farmbios_message(destination, metadata,
                                       callback_id=callback_record.identifier)
        return OutgoingMessage(message_list=[farmbios_msg],
                               callback_record=callback_record)


    def dispatch_message(self, outgoing_msg: OutgoingMessage):
        """
           Register callbacks and send any outgoing messages.
           :param outgoing_msg: Self explanatory.
        """
        # For now, we are assuming that all calls to this method
        # have a callback record in their outgoing messages.
        self.register_callback(outgoing_msg.callback_record)    

        # Check the message destination module
        destination = outgoing_msg.callback_record.request_dispatch
        if destination == mod.SENSOR:
            sensor_conn = self.config.sensor_conn 
            self.route_message(destination, sensor_conn,
                               self.config.sensor_address,
                               outgoing_msg.message_list)
        elif destination == mod.STORAGE:
            storage_conn = self.config.storage_conn
            self.route_message(destination, storage_conn,
                               self.config.storage_address,
                               outgoing_msg.message_list)
        elif destination == mod.COMPUTE:
            compute_conn = self.config.compute_conn
            self.route_message(destination, compute_conn,
                               self.config.compute_address,
                               outgoing_msg.message_list)
        elif destination == mod.ACTUATION:
            actuation_conn = self.config.actuation_conn
            self.route_message(destination, actuation_conn,
                               self.config.actuation_address,
                               outgoing_msg.message_list)
        else:
            self.log("Unknown destination %s\n" % destination)


    def register_callback(self,
                          callback_record: CallBackRecord
                         ):
        """
           Register a callback for a module.
           :param callback_record: The state for returning to the callback.
        """
        #callback_id = callback_record.identifier
        #callback_object = callback_tuple[1]
        self.call_backs[callback_record.identifier] = callback_record


    def send_messages(self,
                      messages: List[FarmBIOSMessage],
                      peer_addr: Union[socket, BaseRPCHandler]):
        """
           Forward any messages from the gRPC call.
           :param messages: The messages to be sent. We put the messages in
                            a list because the CowsOnFitbits app occasionally
                            sends multiple messages as part of a response.
           :param peer_addr: The connection object to the remote peer.
        """ 
        if type(peer_addr) == socket:
            if peer_addr in self.net_mgr.message_queues:
                queue = self.net_mgr.message_queues[peer_addr]
                for message in messages:
                    resp_size = message.ByteSize()
                    serialized_response = _VarintBytes(resp_size)
                    serialized_response += message.SerializeToString()
                    queue.put(serialized_response)

                    # Check if connection is being watched as writable
                    if not(peer_addr in self.net_mgr.outputs):
                        self.net_mgr.outputs.append(peer_addr) 

        else: # Local message that should fall through
            # TODO: Check whether fall-through messages are supposed to be
            #       singular for most applications..
            for message in messages:
                return peer_addr.handle_message(message)


    def process_message(self,
                        message: FarmBIOSMessage,
                        return_addr: Any = None):
        """
           Process a message from the wire.
           :param message: The deserialized message.
           :param return_addr: The caller to return to about any responses.
        """
        msg_type = message.WhichOneof("farmbios_msg_types")
        msg_type = self.handler_mapping[msg_type]

        # First and foremost check that this is not a call back
        callback_id = message.callback.identifier
        self.log("Received callback ID %s\n" % callback_id)
        if (callback_id != None) and (callback_id in self.call_backs):
            callback_struct = self.call_backs[callback_id]

            # Double and triple check before contacting the handler
            if callback_struct.request_dispatch == msg_type:
               self.log("Requested dispatch matches return msg: %s\n" \
                                                                    % msg_type)

               # Swap the return addresses
               return_addr = callback_struct.eventual_return_addr
               self.log("Eventual return addr %s\n" % return_addr)

               # Finally make the call to the handler
               # As of now, the callback returned here is not useful
               handler = self.handlers[callback_struct.register_module] 
               responses, callback = handler.handle_message(message,
                                      callback_func=callback_struct.next_call)
               if (type(return_addr) == socket) and (responses != None):
                   self.send_messages(responses, return_addr)

               # Get rid of the callback when the last response is received.
               if message.callback.isFinalResponse == True:
                   del self.call_backs[callback_id]
               
        # Incoming requests
        elif msg_type in self.handlers.keys(): # Known message type.
            self.log("Received a {} message".format(msg_type))
            if type(return_addr) == socket:
                handler = self.handlers[msg_type]
                responses, callback = handler.handle_message(message,
                                                             return_addr)

                # Check if any call backs need to be registered.
                # The presence of a call back is mutually exclusive
                # with the presence of a response for incoming requests.
                if callback != None:
                    self.register_callback(callback)

                # Check if responses need to be sent over the network
                if responses != None:
                    self.send_messages(responses, return_addr)
        else:
            self.log("Unexpected %s message\n" % msg_type)
