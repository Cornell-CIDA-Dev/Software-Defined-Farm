# System imports
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from time import time, sleep
from typing import Any, Dict


# Local packages
from sdf.compute.base_compute import ComputeModule
from sdf.eval.utils.timer import Timer
from sdf.farmbios.base_handler import BaseRPCHandler 
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import CallType
from sdf.helper_typedefs import Modules as mod
from sdf.network.network_controller import NetworkController 
from sdf.utils.user_input import create_request
from sdf.wineguard.callback_enum_defs import WineGuardComputeCallBacks \
                                             as wing_co_cb 
from sdf.wineguard.proto.wineguard_pb2 import ExperimentResult
from sdf.wineguard.wineguard_config import WineGuardComputeConfig 

# Third party packages
from azureml.core import Dataset, Workspace


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

TEN_SECONDS = 10

# @brief: The trainer module for the WineGuard application.
class WineGuardTrainer(ComputeModule):

    def __init__(self,
                 config: WineGuardComputeConfig,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config


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
        result_msg = ExperimentResult()
        result_msg.ParseFromString(message.data)
        summary = result_msg.resultSummary
        if (type(summary) == str) and ("portal" in summary):
            self.log("\nResult can be seen at %s\n" % summary)
        else:
            self.log("\nResult: %s\n" % summary)

        return None, None


    def run(self,
            dispatcher: Any):
        """
           Run the thread for listening to user requests
           :param dispatcher: The dispatcher for incoming/outgoing messages.
        """

        # Get a pointer to the network controller
        net_ctrl = self.config.net_ctrl

        # A pool of threads to be used for file and message checks. 
        pool = ThreadPoolExecutor(1)

        # A lit of all threads that will need to register the exit signal
        exitable_module_threads = []

        # Run a thread whose job is to check for new messages.
        spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The WineGuard trainer module currently has no
        # threads, so the only exitable thread is the networking thread
        exitable_module_threads.append(net_ctrl)

        # Sleep a bit before starting analytics
        sleep(TEN_SECONDS)

        # NOTE: We may need to replicate this in the other modules
        # unless the order requires the set up of the dispatcher to
        # be after some other action (e.g. config back and forth)
        self.set_dispatcher(dispatcher)

        # Run experiment
        self.submit_experiments(1)

        # Await user exit request.
        while True:
            request = create_request()
            print("Received a signal to exit, releasing resources\n")
            for running_module in exitable_module_threads:
                running_module.exit_signal = True
            break

        # Wait on all the threads to exit
        pool.shutdown(wait=True)


    def submit_experiments(self, num: int):
        """
           Run a given number of training experiments.
           :param num: The number of experiments to run.
        """
        for index in range(num):
            experiment_number = index + 1
            experiment_name = "Edge Wineguard Experiment: " + str(experiment_number)
            timer = Timer("Timer for " + experiment_name)
            print(experiment_name)
            timer.start()
            self.analytics()
            timer.stop()
            print("Sleeping for %d seconds\n" % TEN_SECONDS)
            sleep(TEN_SECONDS)

    def analytics(self):
        """
           Submit a model training experiment.
        """
        compute_msg = ComputeRPC()
        compute_msg.procedure.call = CallType.ANALYTICS
        exp_name = self.config.exp_setup.experimentName
        exp_name = 'farmbioswineguard-' + str(date.today()) 
        exp_name += '-' + str(int(time()))
        self.config.exp_setup.experimentName = exp_name
        compute_msg.proc_args = self.config.exp_setup.SerializeToString()

        # Register a call back to process the results
        outgoing_msg = self.dispatcher.compose_outbound(compute_msg,
                                                        mod.COMPUTE,
                                                        mod.COMPUTE,
                                                        wing_co_cb.PROCESS_RESULTS
                                                       )
        self.dispatcher.dispatch_message(outgoing_msg)

        # Insert model training/registration stuff somewhere here.


    def get_workspace(self, args):
        """ 
            Set up the workspace configuration.
        """
        pass
