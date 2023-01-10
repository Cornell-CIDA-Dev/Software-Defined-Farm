# System packages
from concurrent.futures import ThreadPoolExecutor
from json import loads


# Local packages
from sdf.dairymgr.dairymgr_sensor import DairyManagerSensor 
from sdf.dairymgr.dairymgr_config import DairyManagerSensorConfig
from sdf.utils.user_input import parse_main_args, create_request
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.sensor_handler import SensorRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# Main method
if __name__ == "__main__":
    
    args =  parse_main_args()
    config_file_path = args['config_file']

    user_snapshot_path = args['snapshot']

    # Read the application config and create the module config object
    config = None
    try:
        with open(config_file_path, 'r') as fd:
            config = loads(fd.read())
            config = DairyManagerSensorConfig(config)
    except FileNotFoundError as error:
        print("Config file %s not found." % config_file_path)
        exit(1)

    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.sensor_address[1])

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Create the snapshot tracker object.
    config.load_snapshot(user_snapshot_path=user_snapshot_path)

    # Create the reader map from sensor names to their readers
    config.create_reader_map()

    # Create the modules to be used
    sensor_module = DairyManagerSensor(config)

    # Create the handlers to be used by the dispatcher
    handlers = { mod.SENSOR: SensorRPCHandler(sensor_module) }

    # Create the RPC dispatcher
    dispatcher = Dispatcher(handlers, config)

    # Set the network controller's dispatcher
    # This is used to pass network messages to the dispatcher.
    net_ctrl.set_dispatcher(dispatcher)

    # Set the dispacher's network manager.
    # This is used by the dispatcher to know which connection
    # queues to put messages in.
    dispatcher.set_network_manager(net_ctrl.net_mgr)

    # Give the compute module access to the dispatcher.
    # The dispatcher is used to send any outgoing messages.
    # Unless the module uses the dispatcher in a complex manner,
    # the dispatcher should take care of all of this.
    sensor_module.set_dispatcher(dispatcher)

    # Check if there sensor provider directories exist
    dirs = sensor_module.are_provider_dirs_present(config.start_dir,
                                                   config.providers)
    if not(any([directory in config.providers for directory in dirs.keys()])):
        print("None of the sensor providers <%s> exist! Exiting...\n" % \
              config.providers)
        exit(0)

    # A pool of threads to be used for file and message checks. 
    pool = ThreadPoolExecutor(3)

    # A list of all threads that will need to register the exit signal
    exitable_module_threads = []

    # Run a thread whose job is to check for new messages.
    spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
    spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
    exitable_module_threads.append(net_ctrl)
    

    # Run a thread whose job is to safeguard the snapshot.
    snapshot_future = pool.submit(config.proc_snapshot.monitor_snapshot_struct)
    snapshot_future.add_done_callback(config.proc_snapshot.check_on_threads)
    exitable_module_threads.append(config.proc_snapshot)
 
    # Run a thread whose job is to check for new files.
    check_future = pool.submit(sensor_module.start_periodic_check,
                               config.start_dir)
    check_future.add_done_callback(sensor_module.check_on_threads)
    exitable_module_threads.append(sensor_module)

    # Take user requests.
    while True:
        request = create_request()
        print("Received a signal to exit, releasing resources\n")
        for running_module in exitable_module_threads:
            running_module.exit_signal = True
        break 

    # Wait on all the threads to exit
    pool.shutdown(wait=True)
