# System imports
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


# Local packages
from sdf.compute.base_compute import ComputeModule
from sdf.eval.utils.timer import Timer
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.wineguard.azuremlstuff.control import get_experiment_url 
from sdf.wineguard.wineguard_config import WineGuardComputeConfig 
from sdf.wineguard.azuremlstuff.src.rf_vines import rf_vines_experiment
from sdf.wineguard.proto.wineguard_pb2 import ExperimentSetup, ExperimentResult
from sdf.utils.user_input import create_request


# Third party packages
from azureml.core import Dataset, Workspace


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: The compute module for the WineGuard application.
class WineGuardCompute(ComputeModule):

    def __init__(self,
                 config: WineGuardComputeConfig,
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
        pool = ThreadPoolExecutor(3)

        # A lit of all threads that will need to register the exit signal
        exitable_module_threads = []

        # Run a thread whose job is to check for new messages.
        spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The WineGuard compute module currently has no
        # threads, so the only exitable thread is the networking thread
        exitable_module_threads.append(net_ctrl)

        # Await user exit request.
        #TODO: Refactor this because it appears to be very common in
        #      all of the modules.
        while True:
            request = create_request()
            print("Received a signal to exit, releasing resources\n")
            for running_module in exitable_module_threads:
                running_module.exit_signal = True
            break

        # Wait on all the threads to exit
        pool.shutdown(wait=True)

        # Keeping this for reference until the code is
        # tested and stable.
        #args = ExperimentSetup()
        #args.ParseFromString(message.compute.proc_args)
        #self.log("\nExperiment setup \n %s" % args)
        #timer = Timer("Analtics Experiment")
        #timer.start()
        #result = self.analytics(args)

        #result = ExperimentResult(resultSummary=result)
        #compute_msg = ComputeRPC()
        #compute_msg.procedure.response = ResponseType.SUCCESS
        #farmbios_msg = get_farmbios_message(msg_type=mod.COMPUTE,
        #                                    metadata=compute_msg,
        #                                    data=result.SerializeToString(),
        #                               callback_id=message.callback.identifier,
        #                                    is_final_response=True)
        #timer.stop()
        #return [farmbios_msg], None


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
        timer = Timer("Analtics Experiment")
        timer.start()
        args = ExperimentSetup()
        args.ParseFromString(message.compute.proc_args)
        self.log("\nExperiment setup \n %s" % args)

        self.ml_workspace = self.get_workspace(args) 
        self.log("ANALYTICS TYPE %s\n" % args.env.localRun)
        #if args.env != None and args.env.localRun == True:

        # To be used for testing
        result = ""
        if args.env != None and args.env.localRun == True:

            # Check if the training data file is already local.
            training_file = args.dataset.trainingFile
            training_path = Path(training_file)
            if not(training_path.exists()):
                # Download the geojson dataset.
                dataset = Dataset.get_by_name(self.ml_workspace,
                                              name=args.dataset.name)
                dataset.download(target_path='.', overwrite=False)
                self.log("DATASET %s DOWNLOADED FROM CLOUD STORAGE" % training_file)
                result = rf_vines_experiment(args.dataset.trainingFile)
                # Remove the dataset to force download on next experiment
                #training_path.unlink()
            else:
               self.log("DATASET %s ALREADY EXISTS LOCALLY" % training_file)
               result = rf_vines_experiment(args.dataset.trainingFile)

            self.log("Result %s\n" % result)
            # TODO: Edit this as appropriate when the script result
            #       format changes from list or any other type.
            result_str = ""
            for index, accuracy in enumerate(result):
                if index < (len(result) - 1):
                    result_str += str(accuracy) + ","
                else:
                    result_str += str(accuracy)
            result = result_str
        else:
            experiment_url = get_experiment_url(self.ml_workspace, args)
            result = experiment_url

        result = ExperimentResult(resultSummary=result)
        compute_msg = ComputeRPC()
        compute_msg.procedure.response = ResponseType.SUCCESS
        farmbios_msg = get_farmbios_message(msg_type=mod.COMPUTE,
                                            metadata=compute_msg,
                                            data=result.SerializeToString(),
                                       callback_id=message.callback.identifier,
                                            is_final_response=True)
        timer.stop()
        return [farmbios_msg], None


    def get_workspace(self, args):
        """ 
            Set up the workspace configuration.
        """
        return Workspace(args.access.subscriptionId,
                         args.access.resourceGroup,
                         args.access.workspaceName
                        )
