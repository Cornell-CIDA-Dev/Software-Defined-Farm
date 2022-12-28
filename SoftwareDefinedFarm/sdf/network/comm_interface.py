# System imports
from abc import ABCMeta, abstractmethod
from typing import Any, Optional


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


#@brief: An abstract class for the communication interface. 
class Comm(metaclass=ABCMeta):


    @abstractmethod
    def send(self,
	     payload: Any,
	     sender: Any,
	     destination: Optional[Any],
	     kw_args: Optional[Any]):
        pass


    @abstractmethod
    def receive(self, sender: Any):
        pass 
