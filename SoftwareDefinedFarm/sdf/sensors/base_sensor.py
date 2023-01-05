# System imports
from abc import abstractmethod
from socket import socket
from typing import Any, Optional


# Local packages
from sdf.design_patterns.observer import Observable
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# A semi-abstract class for monitoring sensing assets.
class SensorModule(Observable):

    def __init__(self, identifier: Optional[Any] = None):
        self.identifier = identifier 
        super().__init__()


    def register(self, observer: Any):
        self.mutex.acquire()
        if observer not in self.observers:
            self.observers.append(observer)
        self.mutex.release()


    def remove_registrations(self, peer: Any = None):
        """
           Remove any connection objects or RPC handlers
           that can no longer receive sensor notifications.
           :param peer: Any specific peer to remove.
        """
        self.mutex.acquire()
        # The common case
        if peer != None:
            target_peer = None
            for observer in self.observers:
                if observer == peer:
                    target_peer = observer 
                    break
            self.observers.remove(target_peer)
            self.log("Unregistered %s\n" % peer)
        else:
            self.observers = []
            self.log("Unregistered all observers")
        self.mutex.release()


    def notify(self, update: FarmBIOSMessage):
        """
           Notify observers of a new update.
           :param update: The update to be communicated.
        """ 
        self.mutex.acquire()
        try:
            if not self.changed:
                return
            else:
                # Make a copy in case synchronous addition of observers.
                #local_copy = self.observers[:]
                #for observer in local_copy:
                for observer in self.observers:
                    if type(observer) == socket: # Connection object 
                        self.dispatcher.send_messages([update], observer)
                    else: # Local object.
                        observer.rcv_sensor_notification(update)
                self.clear_changed()
        finally:
            self.mutex.release()


    @abstractmethod
    def run(self,
             *args: Any,
             **kwargs):
        """
           A method for running the sensor module's checks.
        """


    @abstractmethod
    def read(self,
             update: Any,
             caller_addr: Any = None,
             **kwargs):
        """
           A method for reading updates requested by the peer.
        """
