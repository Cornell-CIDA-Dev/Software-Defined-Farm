# System imports
from copy import copy
from socket import socket, SHUT_RDWR, error
from queue import Queue
from typing import Dict, Tuple


# Local packages
from sdf.network.status import CommunicationStatus as comstatus
from sdf.utils.universal_base_class import UniversalBase 


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


#@brief: A base class for managing connections and message queues. 
class NetworkManager(UniversalBase):

    """
       :param incoming_connections: A dictionary.
    """
    def __init__(self,
                 incoming_connections: Dict = {}
                ):
        super().__init__()
        self.incoming_connections = incoming_connections
        self.outgoing_connections = {}
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.peers = [] 


    def add_remote_peer(self, addr_tuple: tuple):
        """
           Add the address of a connected remote peer.
           :param addr_tuple: The IP and port of the remote peer.
        """
        self.peers.append({'hostname': addr_tuple[0],
                           'port': addr_tuple[1]})


    def add_connection(self,
                       connection: socket,
                       return_address: tuple = None,
                       landing_address: Tuple[str, int] = None,
                       outgoing: bool = False
                       ):
        """
           Add an incoming connection to the lookup dictionary.
           :param connection: A socket object.
           :param return_address: The IP,Port tuple to reach the incoming peer.
           :param landing_address: The IP,Port tuple used to connect to peer.
           :param outgoing: A boolean.
        """
        self.inputs.append(connection)
        self.outputs.append(connection)
        self.message_queues[connection] = Queue()
        if outgoing:
            self.outgoing_connections[landing_address] = connection 
        else:
            self.incoming_connections[connection] = return_address


    def remove_all_connections(self):

       for conn, address in self.incoming_connections.items():
           self.log("Shutting down incoming conn %s\n" % conn)
           conn.shutdown(SHUT_RDWR)
           conn.close()

       for port, conn in self.outgoing_connections.items():
           self.log("Shutting down outgoing conn %s\n" % conn)
           conn.shutdown(SHUT_RDWR)
           conn.close()


    def remove_connection(self, connection: socket):
        """
           Remove an active connection from the lookup table.
           :param connection: A socket object.
        """
        if connection in self.incoming_connections:
            self.log("Closing incoming connection from %s \n" % connection)
            del self.incoming_connections[connection]
            self.inputs.remove(connection)
        else:
            self.log("Closing outgoing connection to %s\n" % connection)
            port = -1
            for out_port, con in self.outgoing_connections.items():
                if con == connection:
                    port = out_port
            del self.outgoing_connections[port]
            self.inputs.remove(connection)
        if connection in self.message_queues:
            del self.message_queues[connection]

        # It may be the case that the connection was already shutdodwn
        # by the peer. Therefore, we need to catch occasional case of
        # Transport End is not connected.
        try:
            connection.shutdown(SHUT_RDWR)
            connection.close()
            self.log("Connection shutdown was successful\n")
        except error as socket_error:
            self.log("Conn Shutdown Error >>>: %s\n" % socket_error.__str__())


    def reset_outgoing_connections(self):
        """
           Shutdown outgoing connections if
           there is no data to send.
        """
        if self.outgoing_connections:
            self.log("Resetting outgoing connections\n")
            conn_copies = copy(self.outgoing_connections)
            for port, conn in conn_copies.items():
               self.remove_connection(conn)
        else:
            self.log("No outgoing connections to reset!\n")
            self.log("Skipping operation...")


    #def check_or_revive_connections(self):
    #    """
    #       Reconnect to any peers that the client knows of.
    #    """
    #    if self.outgoing_connections:
    #        return comstatus.SUCCESS
    #    elif not(self.outgoing_connections) and self.peers:
    #        self.log("Attempting to re-establish old connections..\n")
 
    #        # Treat the Internet being out as the common case .
    #        any_connection = comstatus.NETWORK_OUTAGE 

    #        for peer in self.peers:
    #            remote_host = peer['hostname']
    #            remote_port = peer['port']

    #            conn = self.client.connect_to_peer(remote_host, remote_port)
    #            if conn != comstatus.SOCKET_ERROR:
    #                self.add_connection(conn, port=remote_port, outgoing=True)
    #                
    #                # At least one connection has been established.
    #                any_connection = comstatus.SUCCESS
    #            else:
    #                self.log("Attempt to reconnect to %s failed.." % peer)
    #        return any_connection 
    #    else:
    #        self.log("No peers have been added to re-establish connections.")
    #        return comstatus.SOCKET_ERROR
