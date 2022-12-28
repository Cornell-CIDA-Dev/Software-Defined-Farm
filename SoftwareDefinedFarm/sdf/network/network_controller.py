# System imports
from select import select
from queue import Empty as queue_is_empty


# Local packages
from sdf.farmbios.dispatcher import Dispatcher
from sdf.network.server import Server
from sdf.network.client import Client
from sdf.network.status import (CommunicationStatus as comstatus,
                               SOCKET_TIMEOUT)
from sdf.network.network_operator import NetworkOperator
from sdf.network.network_manager import NetworkManager
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase 


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief A class for the network control layer. 
class NetworkController(ThreadedUniversalBase):

    """
       The representation of a network emulator.
    """
    def __init__(self):
      super().__init__()


    def create_components(self, port: int):
        """
           Create all the components needed for a successful emulation.
           :param port: An integer.
        """
        # Create server and client.
        self.server = Server(port)
        self.client = Client()
    
        # Create the network operator and manager.
        self.net_op = NetworkOperator()
        self.net_mgr = NetworkManager()


    def set_dispatcher(self, dispatcher: Dispatcher):
        """
           Set the dispacher for RPC calls.
           :param dispacher: Self explanatory.
        """
        self.dispatcher = dispatcher
    

    def spin_server_forever(self):
        """
           Listen for new connections and process new data.
        """
        self.server.bind_server()
    
        # Initialize inputs and outputs for selector
        self.net_mgr.inputs.append(self.server.server_socket)
        error_statuses = [comstatus.SOCKET_ERROR, comstatus.NO_DATA]
    
        while self.net_mgr.inputs:
            readable, writable, exceptional = select(self.net_mgr.inputs,
                                                     self.net_mgr.outputs,
                                                     self.net_mgr.inputs, 1)
            if self.exit_signal:
                # Remove any connections registered as observers
                self.dispatcher.unregister(all_conns=True)

                self.net_mgr.remove_all_connections()
                self.log("Network layer registered exit signal...\n")
                return
            for incoming in readable:
                self.log("Readables %s\n" % readable)
                if incoming is self.server.server_socket:
                    connection, client_address = incoming.accept()
                    self.log("New connection with peer %s at port %s\n" \
                          % (client_address[0], client_address[1]))
                    connection.settimeout(SOCKET_TIMEOUT)
                    self.net_mgr.add_connection(connection, client_address)
                else:
                    payload = self.net_op.receive(incoming) 
                    if payload in error_statuses:
                        if incoming in self.net_mgr.outputs:
                            self.net_mgr.outputs.remove(incoming)
                        # Remove the connection if it's registered as observer
                        self.dispatcher.unregister(peer=incoming)

                        # Remove the connection from the list being managed.
                        self.net_mgr.remove_connection(incoming)
                    else:
                        if not incoming in self.net_mgr.outputs:
                            self.net_mgr.outputs.append(incoming)
                        self.dispatcher.process_message(payload, incoming)
                        self.log("PROCESSING MESSAGE IS DONE\n")
            for ready in writable:
                if ready in self.net_mgr.message_queues:
                    try:
                        outgoing_msg = self.net_mgr.message_queues[ready].get_nowait()
                    except queue_is_empty:
                        self.log("No message in %s's queue atm" % ready)
                        self.net_mgr.outputs.remove(ready)
                    else:
                        status = self.net_op.send(outgoing_msg, ready)
                        self.log("Sending status %s\n" % status)
                elif ready in self.net_mgr.outputs:
                     self.net_mgr.outputs.remove(ready)
            for exception in exceptional:
                self.log("Connection to %s ran into an exception\n" % exception.getpeername())
                if exception in self.net_mgr.outputs:
                    self.net_mgr.outputs.remove(exception)
                # Remove the connection if it's registered as observer
                self.dispatcher.unregister(peer=incoming)

                # Remove the connection from the list being managed.
                self.net_mgr.remove_connection(exception)
