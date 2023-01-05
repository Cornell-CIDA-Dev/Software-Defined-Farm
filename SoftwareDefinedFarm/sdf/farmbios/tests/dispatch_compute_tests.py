# System imports
import inspect
import unittest


# Local packages
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.compute_pb2 import ComputeRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.farmbios.tests.dispatch_factory import DispatcherFactory
from sdf.farmbios.tests.utils import check_result 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for testing the compute dispatcher.
class TestComputeDispatch(unittest.TestCase):

    def setUp(self):
        # Create the dispatcher
        self.dispatch = DispatcherFactory()
        self.valid_responses = [ResponseType.SUCCESS,
                                ResponseType.ERROR,
                                None]


    def test_compute_run(self):
        """ Test the dispatch for storage PULL interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        compute_msg = ComputeRPC()
        compute_msg.procedure.call = CallType.RUN
        farmbios_msg = get_farmbios_message("compute", compute_msg)
        
        # RUN should return SUCCESS or ERROR
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                # May eventually remove this if the call returns something.
                self.dispatch.process_message(result)
