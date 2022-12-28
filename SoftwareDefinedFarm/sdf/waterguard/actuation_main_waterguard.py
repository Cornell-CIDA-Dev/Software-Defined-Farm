# System packages
from json import loads


# Local packages
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.actuation_handler import ActuationRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.network_controller import NetworkController 
from sdf.utils.user_input import parse_main_args
from sdf.waterguard.waterguard_actuation import WaterGuardActuation 
from sdf.waterguard.config.actuation import WaterGuardActuationConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# Main method
if __name__ == "__main__":
    
    args =  parse_main_args()
    config_file_path = args['config_file']

    # Read the application config and create the module config object
    config = None
    try:
        with open(config_file_path, 'r') as fd:
            config = loads(fd.read())
            config = WaterGuardActuationConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.actuation_address[1])

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Create the modules to be used
    actuation_module = WaterGuardActuation(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = { mod.ACTUATION: ActuationRPCHandler(actuation_module) }

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Run the actuation module
    actuation_module.run(dispatcher)
