# System packages
from concurrent.futures import ThreadPoolExecutor
from json import loads


# Local packages
from sdf.farmbios.config_handler import ConfigRPCHandler
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.compute_handler import ComputeRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 
from sdf.utils.user_input import parse_main_args
from sdf.waterguard.config.compute import WaterGuardComputeConfig 
from sdf.waterguard.waterguard_compute import WaterGuardCompute 


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
            config = WaterGuardComputeConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.compute_port)

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Set the connection to the (remote) storage module
    status, config.storage_conn = config.get_or_set_peer_conn(mod.STORAGE,
                                                      config.storage_address)

    # Set the connection to the (remote) sensor module
    status, config.sensor_conn = config.get_or_set_peer_conn(mod.SENSOR,
                                                     config.sensor_address)

    # Set the connection to the (remote) actuation module
    status, config.actuation_conn = config.get_or_set_peer_conn(mod.ACTUATION,
                                                      config.actuation_address)
    
    # Create the modules to be used
    compute_module = WaterGuardCompute(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = {
                mod.COMPUTE: ComputeRPCHandler(compute_module),
                mod.CONFIG: ConfigRPCHandler(config)
               } 

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Give the WaterGuard module access to the dispatcher to start the config.
    compute_module.set_dispatcher(dispatcher)
    compute_module.start_registration()

    # Run the compute module
    compute_module.run(dispatcher)
