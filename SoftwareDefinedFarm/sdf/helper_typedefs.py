from enum import Enum
from collections import namedtuple


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class SensorInputs(Enum):
    LOCAL_SERIAL = 1
    LOCAL_DIGITAL = 2
    LOCAL_FILE = 3
    REMOTE_REST = 4
    REMOTE_FTP = 5 


class SensorOutputs(Enum):
    LOCAL_FILE = 1
    REMOTE_STORAGE = 2
    REMOTE_ANALYTICS = 3


class StorageTypes(Enum):
    LOCAL_AZURE_STORAGE_EMULATOR = 1
    # When eventually supported
    LOCAL_POSTGRES_DB = 2
    REMOTE_AZURE_TABLE = 3
    REMOTE_CORNELL_REDCLOUD = 4
    # If we eventually move from red cloud
    REMOTE_AZURE_COSMOS_DB = 5


class Analytics(Enum):
    LOCAL_IOTEDGE_MODULES = 1
    REMOTE_AZURE_FUNCTIONS = 2 
    REMOTE_AZURE_ML_PIPELINES = 3


class Actuators(Enum):
    RASPBERRY_PI = 1
    ML_REPORT = 2


class FarmTypes(Enum):
    DAIRY = 1
    APPLE = 2
    VINEYARD = 3
    ROW_CROP = 4


# Initializes a callback record to be registered with the dispatcher.
# The dispatcher keys the request with a unique uuid that will be returned
# with the response.   
# Before calling any appropriate handlers, the dispatcher will check if the
# response is registered as a callback for a given handler.
# param: eventual_return_address: is the original caller
# param: request_dispatch: the module to send the intermediate request to
#                          the dispatcher should know how to contact this
#                          module as a local object or remote connection 
# param: register_module:  the module handler to pass the results to if and
#                          when the request ever returns. 
# param: next_call:        The call where to resume the callback execution 
# param: registration_ts:  the timestamp to keep track of when registrations
#                          should be removed because the callee never got
#                          back to the registering module.
CallBackRecord = namedtuple('CallBackRecord', ['eventual_return_addr',
                                               'request_dispatch',
                                               'register_module',
                                               'next_call',
                                               'registration_ts',
                                               'identifier'])

# Definitions for module raw strings
# This allows for cleaner development by using enums
class Modules(Enum):
    SENSOR = "sensor"
    STORAGE = "storage"
    COMPUTE = "compute"
    ACTUATION = "actuation"
    CONFIG = "config"


# Initialize a tuple containing a list of messages and
# a (possibly empty) callback record to be put into the dispatch queue.
# These tuples will be pulled in a dispatch thread which registers the
# callback (if any) and then send the list of messages.
OutgoingMessage = namedtuple('OutgoingMessage', ['message_list',
                                                 'callback_record'])
