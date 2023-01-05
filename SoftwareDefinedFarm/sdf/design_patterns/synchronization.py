# System imports
import threading
from typing import Any, Optional


# Local imports
from sdf.utils.universal_base_class import UniversalBase
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase


__author__ = "Bruce Eckel & Friends"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Bruce Eckel & Friends"]
__adapted__ = ["https://python-3-patterns-idioms-test.readthedocs.io/\
                en/latest/Observer.html"]


# @brief: Emulation of Java's 'synchronized' keyword for methods.
def synchronized(method: Any):
    def f(*args):
        self = args[0]
        self.mutex.acquire()
        try:
            if len(args) > 1:
                return method(self, args[1:])
            else:
                return method(self)
        finally:
            self.mutex.release()
    return f


# @brief: Emulation of Java's 'synchronized' keyword for an entire class.
def synchronize(klass, names: Optional[str] = None):
    """
       Synchronize methods in the given class.
       :param names: The select methods to synchronize.
    """
    if not(names == None):
        names = names.split() 

    for (name, val) in klass.__dict__.items():
        if callable(val) and name != '__init__' and \
            (names == None or name in names):
            #print("Synchronizing %s\n" % name)

            # New way of setting said attributes
            setattr(klass, name, synchronized(val))


# @brief: The base class to inherit from and get a mutex
class Synchronization(ThreadedUniversalBase):
    def __init__(self):
        super().__init__()
        self.mutex = threading.RLock()
