# System imports
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from platform import node
from os import environ
from time import ctime, sleep, time
from typing import Any, Dict
from socket import gethostname


# Local packages
from sdf.compute.base_compute import ComputeModule
from sdf.utils.timer import Timer
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import CallType
from sdf.helper_typedefs import Modules as mod
from sdf.wineguard.callback_enum_defs import WineGuardComputeCallBacks \
                                             as wing_co_cb 
from sdf.wineguard.proto.wineguard_pb2 import EarthClouResult 
from sdf.wineguard.sharpeningcloud.sharpening_cloud_config import SharpeningRequestConfig 


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

TEN_SECONDS = 10

# @brief: The request module for WineGuard 2.0 app
class SharpeningRequest(ComputeModule):

    def __init__(self,
                 config: SharpeningRequestConfig,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config
        self.timer = None
        if node() == "":
            hostname = gethostname()
        else:
            hostname = node()
  
        # self.result_file = hostname + '-sharpening-requests-' + str(date.today())
        self.result_file = hostname + "-" + environ['TOTAL_EXPERIMENTS']
        self.result_file += "-sharpening-requests-" + str(date.today())
        # Get the hour, minute, and second
        self.result_file += "-" + str(ctime()).split(" ")[3]

        # Boolean to gatekeep how experiments are submitted
        self.ongoing_experiment = False


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def handle_callback(self,
                        message: FarmBIOSMessage,
                        callback_func: wing_co_cb,
                        **kwargs):
       """
           Call the appropriate handler for compute module call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       self.log("HANDLING CALL BACK FOR: %s\n" % callback_func.name)
       if callback_func == wing_co_cb.PROCESS_RESULTS:
           return self.process_results(message)
       else:
           self.log("Unknown call back %s\n" % callback_func.name)
           return None, None


    def process_results(self, message: FarmBIOSMessage):
        """
           Process the results from the training/prediction run.
           :param message: The message from the wire.
        """
        # TODO: Here the results will be either a link to the EarthCloud portal or a link to S3 in case of Dynamo DB.
        result_msg = EarthClouResult()
        result_msg.ParseFromString(message.data)
        summary = result_msg.result
        self.log("\nResult: %s\n" % summary)

        # Clock the end of an experiment
        self.timer.stop(self.result_file)
        # Reset the ongoing experiment flag to enable the next experiment to start
        self.ongoing_experiment = False

        return None, None


    def run(self,
            dispatcher: Any):
        """
           Run the thread for listening to incoming requests
           :param dispatcher: The dispatcher for incoming/outgoing messages.
        """

        # Get a pointer to the network controller
        net_ctrl = self.config.net_ctrl

        # A pool of threads to be used for file and message checks. 
        self.thread_pool = ThreadPoolExecutor(1)

        # Add the trainer module to the list of threads that will exit =
        # upon receving an interrupt signal
        self.exitable_module_threads.append(self)

        # Run a thread whose job is to check for new messages.
        spin_thread_future = self.thread_pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The WineGuard trainer module currently has no
        # threads, so the only exitable thread is the networking thread
        self.exitable_module_threads.append(net_ctrl)

        # Sleep a bit before starting analytics
        sleep(TEN_SECONDS)

        # NOTE: We may need to replicate this in the other modules
        # unless the order requires the set up of the dispatcher to
        # be after some other action (e.g. config back and forth)
        self.set_dispatcher(dispatcher)

        # Run experiments
        # The number of experiments is defined in the container yaml
        total_experiments = int(environ['TOTAL_EXPERIMENTS'])
        self.submit_experiments(total_experiments)

        # Await interrupt signal.
        while self.exit_signal == False:
            # Sleep to avoid consuming cycles
            sleep(5)

        # Wait on all the threads to exit
        self.thread_pool.shutdown(wait=True)


    def submit_experiments(self, num: int):
        """
           Run a given number of training experiments.
           :param num: The number of experiments to run.
        """
        for index in range(num):
            experiment_number = index + 1
            experiment_name = "Sharpening Request: " + str(experiment_number)
            # Clock the start of an experiment
            self.timer = Timer("Timer for " + experiment_name)
            self.log(experiment_name)
            self.timer.start()
            self.ongoing_experiment = True
            self.analytics()
            while self.ongoing_experiment and not(self.exit_signal):
                sleep_time = int(TEN_SECONDS/2)
                self.log("Ongoing experiment %s" % experiment_number)
                self.log("Sleeping for %d seconds before next one\n" % sleep_time)
                sleep(sleep_time)


    def analytics(self):
        """
           Submit a model training experiment.
        """
        compute_msg = ComputeRPC()
        compute_msg.procedure.call = CallType.ANALYTICS
        # TODO: Change the definitions of configs to go with requests
        exp_name = 'sharpening-request-' + str(date.today())
        exp_name += '-' + str(int(time()))
        self.config.earth_cloud.request.name = exp_name
        compute_msg.proc_args = self.config.earth_cloud.request.SerializeToString()

        # Register a call back to process the results
        outgoing_msg = self.dispatcher.compose_outbound(compute_msg,
                                                        mod.COMPUTE,
                                                        mod.COMPUTE,
                                                        wing_co_cb.PROCESS_RESULTS
                                                       )
        self.dispatcher.dispatch_message(outgoing_msg)

        # Insert model training/registration stuff somewhere here.
