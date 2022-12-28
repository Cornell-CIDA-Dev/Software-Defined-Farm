# System imports
from abc import ABCMeta, abstractmethod
from typing import Any, Optional


# Local packages
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The abstract class for all actuations/actuators that a farm can have.
class ActuationModule(ThreadedUniversalBase, metaclass=ABCMeta):

    def __init__(self,
                 location: Optional[Any] = None,
                 *args: Any,
                 **kwargs: Any):
        """ 
            Note: Do not instantiate this directly.
            Extend the class for application specific purposes.
            :param location: The notion of where the module is running.
        """
        self.location = location
        if args:
            self.name = args.name
        super().__init__()


    @abstractmethod
    def activate(self,
                 *args: Any,
                 **kwargs: Any):
        pass


    @abstractmethod
    def run(self):
        """
           A method for running the module.
        """
        pass
