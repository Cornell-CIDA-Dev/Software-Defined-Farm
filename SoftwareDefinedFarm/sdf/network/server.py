# System imports
from socket import (socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR)


# Local packages
from sdf.network.status import (SOCKET_TIMEOUT, ALL_INTERFACES)


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for responding to incoming messages.
class Server:

    def __init__(self, port: int):
        """
            Initialize a server instance on given port.
            :param port: The application's port.
        """
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        #self.buffer = bytearray()


    def bind_server(self):
        """
            Bind the server to listen for connections.
        """
        try:
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.server_socket.bind((ALL_INTERFACES, self.port))
            self.server_socket.listen(10)
            self.server_socket.settimeout(SOCKET_TIMEOUT)
        except Exception as e:
            print("Exception binding server -> %s\n" % e)
            exit(1)
