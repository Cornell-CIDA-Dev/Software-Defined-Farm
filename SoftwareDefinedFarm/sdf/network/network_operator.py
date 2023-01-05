# System imports
from socket import error, socket


# Local packages
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.network.client import Client 
from sdf.network.comm_interface import Comm
from sdf.network.status import (CommunicationStatus as comstatus,
                                BYTE_LIMIT, MESSAGE_SIZE, ZERO_BYTES)


# Third party packages
from google.protobuf.internal.decoder import _DecodeVarint32


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class that handles core network operations.
class NetworkOperator(Comm):
    
    def __init__(self):
        Comm.__init__(self)
        self.buffer = bytearray()


    def receive(self, conn_socket: socket):
        """
           Receive and deserialize a payload from the wire.
           :param conn_socket: The socket to receive from.
        """
        payload = FarmBIOSMessage() 
        message_len, start = self.read_from_buffer(conn_socket)
        if start == None:
             return message_len
        print("Buffer length before parsing %s\n" % len(self.buffer))
        payload.ParseFromString(self.buffer[start:start + message_len])
        self.buffer = bytearray()
        return payload


    def read_from_buffer(self, conn_socket: socket):
        """
            Read from the server buffer until end of message.
            :param conn_socket: The socket to read from.
        """
        print("READING FROM BUFFER\n")
        status, total_read = self.check_incoming_bytes(conn_socket, MESSAGE_SIZE)
        if status != comstatus.SUCCESS: 
            return status, None

        start = 0
        message_len, start_pos = _DecodeVarint32(self.buffer, start)
        message_chunk = len(self.buffer) - start_pos
        if message_chunk < message_len:
            missing_bytes = message_len - message_chunk
            print("Receiving %s missing bytes\n" % missing_bytes)
            self.buffer = bytearray(self.buffer)
            if missing_bytes < BYTE_LIMIT:
                print("Missing bytes: %d < limit: %d" % (missing_bytes,
                                                         BYTE_LIMIT))
                while (missing_bytes > ZERO_BYTES):
                    status, total_read = self.check_incoming_bytes(
                                                                   conn_socket,
                                                                   missing_bytes)
                    missing_bytes -= total_read

                    if status != comstatus.SUCCESS: 
                        print("Possible receive error!: %s\n" % status)
            else:
                print("Missing bytes: %d > limit: %d" % (missing_bytes,
                                                         BYTE_LIMIT))
                while (missing_bytes > ZERO_BYTES):
                    if missing_bytes > BYTE_LIMIT:
                        next_size = BYTE_LIMIT
                    else:
                        next_size = missing_bytes
                    status, total_read = self.check_incoming_bytes(conn_socket,
                                                                   next_size)
                    if total_read == BYTE_LIMIT:
                        missing_bytes -= BYTE_LIMIT
                    else:
                        missing_bytes -= total_read
                    
                    if status != comstatus.SUCCESS:
                        print("Possible receive error!: %s\n" % status)

        self.buffer = bytes(self.buffer)
        print("Message length: %s\n" % message_len)
        return message_len, start_pos


    def check_incoming_bytes(self,
                             conn_socket: socket,
                             size: int
                            ):
         """
            Catch any errors re: the incoming bytes
            :param conn_socket: The socket to receive from.
            :param size: The max number of bytes to receive.
            :rtype: A tuple of the status and bytes read.
         """
         try:
             incoming_bytes = conn_socket.recv(size)
             if len(incoming_bytes) == ZERO_BYTES:
                  print("No data received....\n")  
                  return comstatus.NO_DATA, ZERO_BYTES
         except error as socket_error:
             print("Receiving Error >>>: %s....\n" % socket_error.__str__())
             return comstatus.SOCKET_ERROR, ZERO_BYTES
         except Exception as ex:
             print("General Receiving Exception >>>: %s\n" % ex.__str__())
             return comstatus.SOCKET_ERROR, ZERO_BYTES
         #print("Read in %d bytes\n" % len(incoming_bytes))

         self.buffer += incoming_bytes
         return comstatus.SUCCESS, len(incoming_bytes) 


    def send(self,
             payload: bytes,
             sender: socket
             ):
        """
           :param payload: A serialized bytestring.
           :param sender: A Socket object.
        """
        try:
            bytes_sent = sender.send(payload)
            print("%s bytes sent...\n" % bytes_sent)
            return comstatus.SUCCESS
        except error as socket_error:
            print("Sending failed with error %s...\n" %
                   error.__str__())
            return comstatus.SOCKET_ERROR
