# System imports
from logging import WARNING


# Local packages
from sdf.utils.universal_base_class import UniversalBase


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]



# @brief: Common base class for classes that are submittable as threads.
class ThreadedUniversalBase(UniversalBase):


    def __init__(self):
        super().__init__()


    def check_on_threads(self, future):
        """
           :param future: The future object associated with a function call.
        """
        ft_exception = future.exception()
        if ft_exception != None: # Future failed somehow
           name = str(self.__class__.__name__)
           msg = "{} raised a < {} > exception\n".format(name, ft_exception.__str__())
           self.log(msg, level=WARNING)
