# System packages
from concurrent.futures import ThreadPoolExecutor
from json import loads
from time import sleep


# Local packages
from sdf.farmbios.config_handler import ConfigRPCHandler
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.sensor_handler import SensorRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 
from sdf.utils.user_input import parse_main_args
from sdf.waterguard.config.sensor import WaterGuardSensorConfig
from sdf.waterguard.waterguard_sensor import WaterGuardSensor 


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
            config = WaterGuardSensorConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.sensor_port)

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Set the storage connection
    status, config.storage_conn = config.get_or_set_peer_conn(mod.STORAGE,
                                                        config.storage_address)

    # Create the modules to be used
    sensor_module = WaterGuardSensor(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = {
                mod.SENSOR: SensorRPCHandler(sensor_module),
                mod.CONFIG: ConfigRPCHandler(config)
               } 

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Give the WaterGuard config and module access to the dispatcher. 
    sensor_module.set_dispatcher(dispatcher)
    config.set_dispatcher(dispatcher)

    # Get the remote config and check for watch table partition.
    config.get_sbdata_config()
    config.get_watch_table_presence()

    # Run the sensor module
    sensor_module.run(dispatcher)
