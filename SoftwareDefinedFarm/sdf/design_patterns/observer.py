# System imports
from abc import abstractmethod
from typing import Any


# Local packages
from sdf.design_patterns.synchronization import synchronize, Synchronization
from sdf.utils.universal_base_class import UniversalBase


__author__ = "Bruce Eckel & Friends"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Bruce Eckel & Friends"]
__adapted__ = ["https://python-3-patterns-idioms-test.readthedocs.io/\
                en/latest/Observer.html"]


# @brief: A module to support the "observer" pattern found in Java.
class Observer(UniversalBase):
    def update(observable, arg):
        """
            Update observers the observable is modified.
            To be overridden in the subclasses
            :param observable: some object.
            :param arg: the object that triggers the nofify_observers.
        """
        pass


class Observable(Synchronization):
    """
        A representation of the observable in relation to its observers.
    """
    def __init__(self):
        self.observers = []
        self.changed = 0
        super().__init__()


    def delete_observer(self, observer: Any):
        self.observers.remove(observer)


    @abstractmethod
    def register(self, observer: Any):
        """
           Register any interested parties.
           :param observer: The local or remote party.
        """

    @abstractmethod
    def notify(self, update: Any = None):
        """
           Notify observers that the object has been changed.
           :param update: Any applicable info that comes with state changes.
        """
        # Find old notify code in base_sensor.py

    def delete_observers(self): self.observers = []
    def set_changed(self): self.changed = 1
    def clear_changed(self): self.changed = 0
    def has_changed(self): return self.changed
    def count_observers(self): return len(self.observers)


# Synchronize the observable class
synchronize(Observable,
            "delete_observer delete_observers set_changed " +
            "has_changed count_observers")
