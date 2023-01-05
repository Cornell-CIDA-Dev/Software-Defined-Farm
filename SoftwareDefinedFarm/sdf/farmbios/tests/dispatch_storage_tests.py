# System imports
import inspect
import unittest
from uuid import uuid4


# Local packages
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.farmbios.proto.storage_pb2 import StorageRPC
from sdf.farmbios.tests.dispatch_factory import DispatcherFactory
from sdf.farmbios.tests.utils import check_result 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for testing the sensor dispatcher.
class TestStorageDispatch(unittest.TestCase):

    def setUp(self):
        # Create the dispatcher
        self.dispatch = DispatcherFactory()
        self.valid_responses = [ResponseType.SUCCESS,
                                ResponseType.ERROR,
                                ResponseType.REQUESTED_DATA,
                                ResponseType.UNKNOWN_ITERATOR,
                                ResponseType.NEXT_ITEM,
                                ResponseType.FEED_ITERATOR,
                                ResponseType.SUBSCRIBE_SUCCESS,
                                ResponseType.PUSH_SUCCESS,
                                ResponseType.NO_DATA,
                                ResponseType.TOPIC_UPDATES,
                                None]


    def test_storage_write(self):
        """ Test the dispatch for storage WRITE interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.WRITE
        random_path = '/mnt/c/random/path/'
        storage_msg.medium.sdf_fs.path = random_path
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # WRITE should return SUCCESS 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)


    def test_storage_read(self):
        """ Test the dispatch for storage READ interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.READ
        random_path = '/mnt/c/random/path/'
        storage_msg.medium.sdf_fs.path = random_path
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # READ should return bytes 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                 # Check that the returned response is REQUESTED_DATA
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_storage_change_feed(self):
        """ Test the dispatch for storage GET_CHANGE_FEED interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.GET_CHANGE_FEED
        storage_msg.medium.sdf_feed.iterator = 'init'
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # GET_CHANGE_FEED should return a new iterator when initiating 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_storage_next(self):
        """ Test the dispatch for storage NEXT interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.GET_NEXT
        storage_msg.medium.sdf_feed.iterator = str(uuid4()) 
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # NEXT should return the next item or nothing
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_storage_subscribe(self):
        """ Test the dispatch for storage SUBSCRIBE interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.SUBSCRIBE
        topics = ['oranges', 'bananas'] 
        storage_msg.medium.sdf_pub_sub.topics.extend(topics)
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # SUBSCRIBE should return success or nothing 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_storage_push(self):
        """ Test the dispatch for storage PUSH interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.PUSH
        topics = ['oranges'] 
        storage_msg.medium.sdf_pub_sub.topics.extend(topics)
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # SUBSCRIBE should return success or nothing 
        results = self.dispatch.process_message(farmbios_msg)

        if results:
            for result in results:
                check_result(self, result)
                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)


    def test_storage_notify(self):
        """ Test the dispatch for storage NOTIFY interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.NOTIFY
        topics = ['oranges', 'bananas'] 
        storage_msg.medium.sdf_pub_sub.topics.extend(topics)
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # NOTIFY should return nothing 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            for result in results:
                check_result(self, result)


    def test_storage_pull(self):
        """ Test the dispatch for storage PULL interface. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        storage_msg = StorageRPC()
        storage_msg.procedure.call = CallType.PULL
        topics = ['oranges'] 
        storage_msg.medium.sdf_pub_sub.topics.extend(topics)
        farmbios_msg = get_farmbios_message("storage", storage_msg) 

        # SUBSCRIBE should return success or nothing 
        results = self.dispatch.process_message(farmbios_msg)
        if results:
            # Check that the returned response is PUSH_SUCCESS
            for result in results:
                check_result(self, result)

                # Check that processed responses return the valid type (None).
                self.dispatch.process_message(result)
