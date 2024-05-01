# System packages
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable, ClassVar, Dict, Optional


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# Brief: Time decorator adapted from https://realpython.com/python-timer/
# Provides a way to time functions by adding it as boiler plate,
# context managers, or decorators.

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

@dataclass
class Timer(ContextDecorator):
    """Time your code using a class, context manager, or decorator"""

    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    text: str = "Elapsed time: {:0.4f} seconds\n"
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)


    def __post_init__(self) -> None:
        """Initialization: add timer to dict of timers"""
        if self.name:
            self.timers.setdefault(self.name, 0)


    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = perf_counter()


    def stop(self,
             path: str = None,
             is_final_experiment: bool = False) -> float:
        """
           Stop the timer, and report the elapsed time
           :param path: The path (if any) where to save the timing.
           :param is_final_experiment: Determines how the final write occurs
        """
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = perf_counter() - self._start_time
        self._start_time = None

        # Add the time for downloading images in S3 as reported by ferg
        elapsed_time += 121

        if path:
            base_file = path.split("/")
            # base_file = base_file[len(base_file)-1]
            with open(path, "a") as fd:
                result = str(elapsed_time) + "\n"
                fd.write(result)

        # Report elapsed time
        if self.logger:
            self.logger(self.name + "\n" + self.text.format(elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time


    def __enter__(self) -> "Timer":
        """Start a new timer as a context manager"""
        self.start()
        return self


    def __exit__(self, *exc_info: Any) -> None:
        """Stop the context manager timer"""
        self.stop()
