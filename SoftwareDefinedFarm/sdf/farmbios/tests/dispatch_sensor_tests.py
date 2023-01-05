# System imports
import inspect
import unittest


# Local packages
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.farmbios.tests.dispatch_factory import DispatcherFactory
from sdf.farmbios.tests.utils import check_result 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for testing the sensor dispatcher.
class TestSensorDispatch(unittest.TestCase):

    def setUp(self):
        # Create the  dispatcher and network controller
        self.dispatch = DispatcherFactory()

        self.valid_responses = [ResponseType.SUCCESS,
                                ResponseType.ERROR,
                                ResponseType.REGISTER_SUCCESS,
                                ResponseType.REQUESTED_DATA,
                                None]


    def test_register_sensor_observer(self):
        """ Test the dispatch for sensor REGISTER interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.REGISTER
        farmbios_msg = get_farmbios_message("sensor", sensor_msg) 

        # Registers should always return success unless something goes wrong. 
        results = self.dispatch.process_message(farmbios_msg) 
        if results:
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_notify_sensor_observer(self):
        """ Test the dispatch for sensor NOTIFY interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.NOTIFY
        farmbios_msg = get_farmbios_message("sensor", sensor_msg)

        # Notifies should return nothing for the caller.
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)


    def test_read_sensor_observer(self):
        """ Test the dispatch for sensor READ interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.READ
        farmbios_msg = get_farmbios_message("sensor", sensor_msg) 

        # READ should return the requested data. 
        results = self.dispatch.process_message(farmbios_msg) 
        if results:
            for result in results:
                check_result(self, result)

        # Check that the returned responses are of the valid type (REQUESTED_DATA).
        for result in results: 
            results = self.dispatch.process_message(result)
