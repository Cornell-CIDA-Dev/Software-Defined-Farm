# System imports
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from time import sleep


# Local packages
from sdf.compute.base_compute import ComputeModule
#from sdf.eval.utils.timer import Timer
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.storage.nasacloudwrappers.nasa_appeears_wrapper import NASAppeearsService 
from sdf.storage.awswrappers.aws_dynamodb_wrapper import DynamoDBService 
from sdf.storage.awswrappers.aws_s3_wrapper import S3Service 
from sdf.wineguard.sharpeningcloud.sharpening_cloud_config import SharpeningRequestConfig 
from sdf.wineguard.proto.wineguard_pb2 import Request, EarthClouResult


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The sharpening compute module for WineGuard 2.0 app
class SharpeningCompute(ComputeModule):

    def __init__(self,
                 config: SharpeningRequestConfig,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config


    def run(self, dispatcher: Any):
        """
           Initialize the experiment using the procedure arguments
           :param message: The message from the wire.
        """
        # Get a pointer to the network controller
        net_ctrl = self.config.net_ctrl

        # A pool of threads to be used for file and message checks.
        self.thread_pool = ThreadPoolExecutor(3)

        # Add the compute module to the list of threads that will exit
        # upon receiving an interrupt signal
        self.exitable_module_threads.append(self)

        # Run a thread whose job is to check for new messages.
        spin_thread_future = self.thread_pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The sharpening compute module currently has no
        # threads, so the only exitable thread is the networking thread
        self.exitable_module_threads.append(net_ctrl)

        # Await user exit request.
        #TODO: Refactor this because it appears to be very common in
        #      all of the modules.
        while self.exit_signal == False:
            # Sleep to avoid consuming cycles
            sleep(5)

        # Wait on all the threads to exit
        self.thread_pool.shutdown(wait=True)


    def analytics(self, message: FarmBIOSMessage):
        """
           Perform the model training and prediction.
           The message is decoupled into the metadata for the experiment.
           The subscription ID, resource group, and workspace name
           are always required no matter the desired run (local,
           cloud) because it may be necessary to download the
           previously uploaded training data.
           :param message: The message from the wire.
        """
        #timer = Timer("Analtics Experiment")
        #timer.start()
        args = Request()
        args.ParseFromString(message.compute.proc_args)
        self.log("\nRequest setup \n %s" % args)

        # Insert logic for issuing requests either to NASA or DynamoDB here
        # POC to pull list of products from EarthCloud
        credentials = {'username': self.config.earth_cloud.access.username,
                       'password': self.config.earth_cloud.access.password
                      }

        nasa_resource = NASAppeearsService(credentials)
        product_list = nasa_resource.get_product_list()
        #self.log("All EarthCloud products %s\n" % product_list)

        
        dynamodb_service = DynamoDBService(self.config)
        table_name = "Images_TestTable"
        table = dynamodb_service.get_table(table_name)
        self.log("Table Name %s\n" % table.table_name)
        self.log("Table Creation Time: %s" % table.creation_date_time)
        self.log("Table Item Count %s\n" % table.item_count)

        # Test getting an existing time in the table
        #item = {'timestamp': 1595142000,
        #        'image_id': 'lodi_1'}
        #self.log("Testing get item for %s\n" % item)
        #item = dynamodb_service.read(table_name, item)['Item']

        # Test downloading an image from S3
        bucket_name = "sharpenedhlsimagery"
        object_name = ""
        local_dest = "local_copy.tif"
        s3_service = S3Service(self.config)
        s3_service.read(bucket_name, object_name, local_dest)


        # Encapsulate results and send them back to the requester
        result = EarthClouResult(result="allgood")
        self.log("Result %s\n" % result)
        compute_msg = ComputeRPC()
        compute_msg.procedure.response = ResponseType.SUCCESS
        farmbios_msg = get_farmbios_message(msg_type=mod.COMPUTE,
                                            metadata=compute_msg,
                                            data=result.SerializeToString(),
                                       callback_id=message.callback.identifier,
                                            is_final_response=True)
        #timer.stop()
        return [farmbios_msg], None
