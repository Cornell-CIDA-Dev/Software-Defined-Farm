# System packages
from json import loads
from time import sleep
from signal import signal, SIGINT


# Local packages
from sdf.utils.user_input import parse_main_args
#from sdf.eval.utils.timer import Timer
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.compute_handler import ComputeRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 
from sdf.wineguard.sharpeningcloud.sharpening_request import SharpeningRequest
from sdf.wineguard.sharpeningcloud.sharpening_cloud_config import SharpeningRequestConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

TEN_SECONDS = 10


# Main method
if __name__ == "__main__":
    
    args =  parse_main_args()
    config_file_path = args['config_file']

    # Read the application config and create the module config object
    config = None
    try:
        with open(config_file_path, 'r') as fd:
            config = loads(fd.read())
            config = SharpeningRequestConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.requester_address[1])

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Set a connection to the (remote) compute module
    status, config.compute_conn = config.get_or_set_peer_conn(mod.COMPUTE,
                                                      config.compute_address)
    # Create the modules to be used
    request_module = SharpeningRequest(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = {
                mod.COMPUTE: ComputeRPCHandler(request_module),
               } 

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Set teh signal handler for the "main" trainer module.
    signal(SIGINT, request_module.signal_handler)

    # Sleep a bit before starting analytics
    sleep(TEN_SECONDS)
    
    # Run the trainer module
    request_module.run(dispatcher)
