# System packages
from concurrent.futures import ThreadPoolExecutor
from json import loads
from random import randint
from socket import socket
from time import sleep


# Local packages
from sdf.dairymgr.dairymgr_compute import DairyManagerCompute 
from sdf.dairymgr.dairymgr_config import DairyManagerComputeConfig 
from sdf.utils.user_input import parse_main_args, create_request
from sdf.farmbios.dispatcher import Dispatcher
from sdf.farmbios.compute_handler import ComputeRPCHandler
from sdf.helper_typedefs import Modules as mod
from sdf.network.network_controller import NetworkController 
from sdf.network.status import CommunicationStatus as comstatus


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
            config = DairyManagerComputeConfig(config)
    except FileNotFoundError as fnf:
        print("Config file %s not found... exiting" % config_file_path)
        exit(1)


    # Create the net_ctrl that drives the underlying network layer sockets.
    net_ctrl = NetworkController()
    net_ctrl.create_components(config.compute_address[1])

    # Set the configuration's network controller
    config.net_ctrl = net_ctrl

    # Create the modules to be used
    compute_module = DairyManagerCompute(config)
                                                
    # Create the handlers to be used by the dispatch.
    handlers = {
                mod.COMPUTE: ComputeRPCHandler(compute_module)
                # TODO: restore this if the compute module ends up asking
                # for a specific set of sensor updates.
                # This setup should be done during the config phase.
                # mod.CONFIG: ConfigRPCHandler(config)
               } 

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
    compute_module.set_dispatcher(dispatcher)

    # Set connection to the sensor module
    status, config.sensor_conn = config.get_or_set_peer_conn(mod.SENSOR,
                                                         config.sensor_address)

    # Set connection to the storage module
    status, config.storage_conn = config.get_or_set_peer_conn(mod.STORAGE,
                                                        config.storage_address)

    while type(config.sensor_conn) != socket:
        timeout = randint(5, 30)
        print("Retrying connection to sensor module in %d seconds\n" % timeout)
        sleep(timeout)

        # Set the connection to the (remote) sensor module
        status, config.sensor_conn = config.get_or_set_peer_conn(mod.SENSOR,
                                                  config.sensor_address)

    # A pool of threads to be used for file and message checks. 
    pool = ThreadPoolExecutor(1)

    # A list of all threads that will need to register the exit signal
    exitable_module_threads = []

    # Add the compute module handler as an exitable thread
    exitable_module_threads.append(handlers[mod.COMPUTE].module)

    # Run a thread whose job is to check for new messages.
    spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
    spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
    exitable_module_threads.append(net_ctrl)

    # Start the registration with the pen capacity sensor
    sleep(5)
    sensor = 'pencap'
    compute_module.start_registration(sensor)

    # Take user requests.
    while True:
        request = create_request()
        print("Received a signal to exit, releasing resources\n")
        for running_module in exitable_module_threads:
            running_module.exit_signal = True
        break 

    # Wait on all the threads to exit
    pool.shutdown(wait=True)
