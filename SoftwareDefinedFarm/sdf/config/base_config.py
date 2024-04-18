# System imports
from typing import Any, Dict, Optional, Tuple


# Local imports
from sdf.farmbios.base_handler import BaseRPCHandler
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.utils.universal_base_class import UniversalBase


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring any module runs.
class BaseConfig(UniversalBase):

    def __init__(self,
                 config: Dict[str, str],
                 **kwargs):
        """
           :param config: The application configuration.
        """
        # Set the module's co-location status relative to other modules
        if 'location' in config and config['location'] == "local":
            self.colocation = True
        else:
            self.colocation = False

        if 'sensorHost' in config:
            self.sensor_address = tuple([ config['sensorHost'],
                                     int(config['sensorPort'])
                                   ])
        if 'storageHost' in config:
            self.storage_address = tuple([ config['storageHost'],
                                      int(config['storagePort'])
                                    ])
        if 'computeHost' in config:
            self.compute_address = tuple([ config['computeHost'],
                                           int(config['computePort'])
                                         ])
        if 'actuationHost' in config:
            self.actuation_address = tuple([ config['actuationHost'],
                                             int(config['actuationPort'])
                                           ])

        super().__init__()


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def handle_callback(self,
                        message: FarmBIOSMessage,
                        callback_func: Any,
                        **kwargs):
       """
           Call the appropriate handler for config call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       pass


    def get_or_set_peer_conn(self,
                             module_type: mod,
                             peer_address: Tuple[str, int] = None,
                             local_handler: Optional[BaseRPCHandler] = None):
        """
           Set the connection to a remote peer module or a local
           version of their RPC handler.
           :param peer_address: The (remote) IP address of the peer module.
           :param module_type: The module being sought for connection. 
           :param local_handler: The RPC handler if calls are fall-through.
           :rtype: A socket connection object or a handler.
        """
        conn = None
        if not(self.colocation):
            net_mgr = self.net_ctrl.net_mgr
            if peer_address in net_mgr.outgoing_connections:
                return comstatus.SUCCESS, net_mgr.outgoing_connections[peer_address]
            else:
                # Treat the Internet being out as a possibility.
                any_connection = comstatus.NETWORK_OUTAGE
                conn_attempt = self.net_ctrl.client.connect_to_peer(peer_address[0],
                                                                    peer_address[1])
                if conn_attempt != comstatus.SOCKET_ERROR:
                    conn = conn_attempt
                    net_mgr.add_connection(conn, landing_address=peer_address,
                                           outgoing=True)
                    net_mgr.add_remote_peer(peer_address)
                    # Connection was successfully established
                    return comstatus.SUCCESS, conn
                else:
                    print("Connection to %s module at %s failed...\n" % \
                                                                (module_type.name,
                                                                 peer_address))
                    print("Connection to be attempted later...\n")
                    any_connection = conn_attempt
                    return any_connection, None
        elif local_handler != None:
            conn = local_handler
        # For local fall-throughs (rare), the status should be None  
        return None, conn
