# System imports
from logging import WARNING
from typing import Any
from signal import Signals


# Local packages
from sdf.utils.universal_base_class import UniversalBase


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]



# @brief: Common base class for classes that are submittable as threads.
class ThreadedUniversalBase(UniversalBase):


    def __init__(self):
        super().__init__()
        self.exitable_module_threads = []
        self.thread_pool = None


    def signal_handler(self, signum, frame):
        """
           A handler to watch for exit signs such as SIGINT and SIGKILL.
           :param signum: The signal number sent.
           :param frame: The stack frame of where the main thread's execution
                         was interrupted.
        """
        signame = Signals(signum).name
        self.log("%s module signal handler called with %s (%s)" %
                      (self.__class__.__name__, signame, signum))

        if self.thread_pool != None:
            # Notify all other threads, if any, to exit
            for running_module in self.exitable_module_threads:
                self.log("Notifying %s module to exit" % running_module.__class__.__name__)
                running_module.exit_signal = True


    def check_on_threads(self, future):
        """
           :param future: The future object associated with a function call.
        """
        ft_exception = future.exception()
        if ft_exception != None: # Future failed somehow
           name = str(self.__class__.__name__)
           msg = "{} raised a < {} > exception\n".format(name, ft_exception.__str__())
           self.log(msg, level=WARNING)
