# System imports
from socket import socket, error, AF_INET, SOCK_STREAM


# Local packages
from sdf.network.status import (CommunicationStatus as comstatus,
                               SOCKET_TIMEOUT)



__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for establishing outgoing connection sockets.
class Client:

    def __init__(self):
        """
            Initialize a client instance on local host.
        """
        self.client_socket = None
        #self.buffer = bytearray()

    def connect_to_peer(self,
                        host: str,
                        port: int
                       ):
        """
            Connect to a remote peer.
            :param host: The peer's ip address.
            :param port: The application's port.
        """
        try:
            new_socket = socket(AF_INET, SOCK_STREAM)
            new_socket.settimeout(SOCKET_TIMEOUT)
            new_socket.connect((host, port))
            return new_socket 
        except error as socket_error:
            print("Client Error >>>: %s" % socket_error.__str__())
            return comstatus.SOCKET_ERROR
