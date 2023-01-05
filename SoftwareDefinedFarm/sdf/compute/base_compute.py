# System imports
from abc import ABCMeta, abstractmethod
from typing import Any, Optional


# Local packages
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The compute module for the FarmBIOS apps.
class ComputeModule(ThreadedUniversalBase, metaclass=ABCMeta):

    def __init__(self,
                 *args: Any,
                 **kwargs: Any):
        """ 
            Note: Do not instantiate this directly.
            Extend the class for application specific purposes.
        """
        super().__init__()


    @abstractmethod
    def run(self):
        """
           A method for running any experiments requested by the peer.
           :param args: The experiment metadata.
        """


    @abstractmethod
    def analytics(self,
                  setup: Any,
                  caller_address: Optional[Any] = None):
        """
           A method for running app-specific analytics.
           :param args: The experiment metadata.
        """


    def notification_sensor_recv(self, context):
        """
           A method for local calls to read sensor updates.
           :param context: The context to read from.
        """
        pass


    def notification_storage_recv(self, new_data):
        """
           A method for processing storage subscription updates.
           :param context: The newly available data.
        """
        pass
