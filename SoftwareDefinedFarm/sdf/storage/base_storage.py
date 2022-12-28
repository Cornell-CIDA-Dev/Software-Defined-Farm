# System imports
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, TypeVar, Dict


# Local packages
from sdf.design_patterns.observer import Observable


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class StorageTypes(Enum):
    LOCAL_AZURE_STORAGE_EMULATOR = 1
    # When eventually supported
    LOCAL_POSTGRES_DB = 2
    LOCAL_AZURE_TABLE = 3
    REMOTE_AZURE_TABLE = 4
    REMOTE_CORNELL_REDCLOUD = 5 
    # If we eventually move from red cloud
    REMOTE_AZURE_COSMOS_DB = 6 


# Type definitions for the path and specifications.
D = TypeVar('D')
I = TypeVar('I')
P = TypeVar('P')
Subscriber = TypeVar('Subscriber')
S = TypeVar('S')
T = TypeVar('T')


# An abstract class for all data operations.
class StorageModule(Observable, metaclass=ABCMeta):

    def __init__(self,
                 *args: tuple,
                 **kwargs: Dict[Any, Any]):
        super().__init__()


    @abstractmethod
    def read(self,
             *args: tuple,
             **kwargs: Dict[Any, Any]):
        """
           Read from a local or remote storage medium.
        """


    @abstractmethod
    def write(self,
              *args: tuple,
              **kwargs: Dict[Any, Any]):
        """
           Write to a local or remote storage medium.
        """


    def change_feed(self):
        """
           Get the change feed for a data container.
        """
        pass
    

    def next(self, iterator: I):
        """
           Get the next item from a continuation.
           :param iterator: The continuation to be used.
        """
        pass


    def subscribe(self,
                  subscriber: Subscriber,
                  topic: T):
        """
           Subscribe to a topic on a storage media.
           :param subscriber: A local or remote peer module.
           :param topic: The topic of interest to the peer module.
        """
        pass


    def push(self,
             topic: T,
             data: D):
        """
           Publish new updates to storage.
           :param topic: The topic of interest to the peer module.
           :param data: The data to stored. 
        """
        pass


    def notify(self,
               subscriber: Subscriber,
               data: D):
        """
           Avail new updates to subscribers.
           :param subscriber: A local or remote peer module.
           :param data: The data to be sent to the subscribers
        """
        pass


    def pull(self,
             topic: T,
             since: S):
        """
           Pull recent updates from storage w/o notification capabilities.
           :param topic: The topic of interest to the peer module.
           :param since: A hash of the last update known to the peer.
        """
        pass


    def run(self,
             *args: Any,
             **kwargs):
        """
           A method for running the storage module.
        """
        pass
