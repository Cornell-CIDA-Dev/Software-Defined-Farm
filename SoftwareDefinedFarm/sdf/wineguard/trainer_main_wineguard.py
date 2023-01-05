# System packages
from json import loads
from time import sleep


# Local packages
from sdf.utils.user_input import parse_main_args, create_request
from sdf.eval.utils.timer import Timer
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.compute_handler import ComputeRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 
from sdf.wineguard.wineguard_trainer import WineGuardTrainer 
from sdf.wineguard.wineguard_config import WineGuardTrainerConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

TEN_SECONDS = 10

def run_experiments(num, module):
    """
       Run a given number of training experiments.
       :param num: The number of experiments to run.
       :param module: The module to send out experiment requests.
    """
    for index in range(num):
        experiment_number = index + 1
        experiment_name = "Edge Wineguard Experiment: " + str(experiment_number)
        #timer = Timer(timer_name)
        print(experiment_name)
        #timer.start()
        module.analytics()
        #timer.stop()
        print("Sleeping for %d seconds\n" % TEN_SECONDS)
        sleep(TEN_SECONDS)

# Main method
if __name__ == "__main__":
    
    args =  parse_main_args()
    config_file_path = args['config_file']

    # Read the application config and create the module config object
    config = None
    try:
        with open(config_file_path, 'r') as fd:
            config = loads(fd.read())
            config = WineGuardTrainerConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.trainer_address[1])

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Set a connection to the (remote) compute module
    status, config.compute_conn = config.get_or_set_peer_conn(mod.COMPUTE,
                                                      config.compute_address)
    # Create the modules to be used
    trainer_module = WineGuardTrainer(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = {
                mod.COMPUTE: ComputeRPCHandler(trainer_module),
               } 

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Sleep a bit before starting analytics
    sleep(TEN_SECONDS)
    
    # Run the trainer module
    trainer_module.run(dispatcher)
