import logging
import inspect

class UniversalBase(object):
    """
      Common base-class for all application objects.
      Takes care of common initilization to provide a consistent view across objects
    """

    def __init__(self, name=None):
        self._objname = name or "{}:{}".format(self.__class__.__module__,
                                               self.__class__.__name__)
#        logging.basicConfig(
#            format = "{levelname:1.1}[{caller_info}]: {message}",
#            level = logging.INFO,
#            style="{"
#        )
#        self._logger = self.create_logger()
        self.exit_signal = False

    @property
    def objname(self):
        return self._objname

#    def create_logger(self):
#        return logging.getLogger(self.objname)

    def log(self, msg, level = logging.INFO):
        """
        Wrapper around python3 logging.log. Allows for standard logging
        across the entire application
        :param msg: str: Message to be logged
        :param level: int: Severity of log. ie. logging.INFO or logging.WARNING
        """
        ##This can be replaced with a print if we want to remove dependency on logger
        #contextual_info = {
        #    "caller_info": "".join([
        #        "%s:" % self.__class__.__module__,
        #        "%s:" % self.__class__.__name__,
        #        "%s:" % inspect.stack()[1].function,
        #        "%s" % inspect.stack()[1].lineno,
        #    ])
        #}
#       # self._logger.log(level=level, msg=msg, extra=contextual_info)
        #print(contextual_info["caller_info"],": ",msg)

        #This can be replaced with a print if we want to remove dependency on logger
        contextual_info = {
            "caller_info": "".join([
                "%s:" % self.__class__.__name__,
                "%s:" % inspect.stack()[1].function,
                "%s" % inspect.stack()[1].lineno,
            ])
        }
#        self._logger.log(level=level, msg=msg, extra=contextual_info)
        print(contextual_info["caller_info"],": ",msg)
