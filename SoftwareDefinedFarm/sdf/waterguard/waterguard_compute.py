# System imports
from concurrent.futures import ThreadPoolExecutor
from typing import Any


# Local packages
from sdf.compute.base_compute import ComputeModule
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.actuation_pb2 import ActuationRPC
from sdf.farmbios.proto.sensor_pb2 import SensorRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.utils.user_input import create_request
from sdf.waterguard.callback_enum_defs import \
                                  WaterGuardComputeCallBacks as watg_comp_cb
from sdf.waterguard.config.compute import WaterGuardComputeConfig
from sdf.waterguard.proto.waterguard_pb2 import (WaterGuardUpdate,
                                                 RequestedReadData,
                                                 TwilioMessage)
from sdf.waterguard.utils import get_storage_rpc


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

# @brief: A class for WaterGuard analytics functions
class WaterGuardCompute(ComputeModule):

    def __init__(self,
                 config: WaterGuardComputeConfig,
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
                        callback_func: Any,
                        **kwargs):
       """
           Call the appropriate handler for compute module call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       self.log("HANDLING CALL BACK FOR: %s\n" % callback_func.name)
       if callback_func == watg_comp_cb.ANALYTICS:
           return self.analytics(message)
       elif callback_func == watg_comp_cb.CONFIRM_REGISTRATION:
           return self.confirm_registration(message)
       else:
           self.log("Unknown call back %s\n" % callback_func.name)
           return None, None


    def start_registration(self):
        """
           Register with the sensor module.
        """
        sensor_msg = SensorRPC()
        sensor_msg.procedure.call = CallType.REGISTER 

        # Register a call back to finish the registration and configuration
        outgoing_msg = self.dispatcher.compose_outbound(sensor_msg,
                                                        mod.COMPUTE,
                                                        mod.SENSOR,
                                             watg_comp_cb.CONFIRM_REGISTRATION)
        self.dispatcher.dispatch_message(outgoing_msg)


    def confirm_registration(self, message: FarmBIOSMessage):
        """
           Process a registration confirmation message from the sensor module.
           Set the configuration passed by the sensor module.
        """
        status = message.sensor.procedure.response
        if status == ResponseType.REGISTER_SUCCESS:
            self.log("SENSOR REGISTRATION WITH SENSOR MODULE WAS SUCCESSFUL")
            self.config.sensorbox_config = {}
            update = WaterGuardUpdate()
            update.ParseFromString(message.sensor.update)
            sensor_config = update.possibleSensors.mapping
            for sensor in sensor_config:
                self.config.sensorbox_config[sensor] = sensor_config[sensor]
            self.log("Sensor box config : %s\n" % self.config.sensorbox_config)
        else:
            self.log("SENSOR REGISTRATION WITH SENSOR MODULE FAILED")
        # No responses to send or callbacks to register
        return None, None


    def run(self, dispatcher: Any):
        """
           Start the threads for the appropriate functions.
           :param dispatcher: The dispatcher of incoming/outgoing messages.
        """
        # Get a pointer to the network controller
        net_ctrl = self.config.net_ctrl

        # A thread pool to be used for checking new network messages
        pool = ThreadPoolExecutor(1)

        # A lit of all threads that will need to register the exit signal
        exitable_module_threads = []

        # Run a thread whose job is to check for new messages.
        spin_thread_future = pool.submit(net_ctrl.spin_server_forever)
        spin_thread_future.add_done_callback(net_ctrl.check_on_threads)
        # Note: The WaterGuard compute module currently has no
        # threads, so the only exitable thread is the networking thread
        exitable_module_threads.append(net_ctrl)

        # Await user exit request.
        while True:
            request = create_request()
            print("Received a signal to exit, releasing resources\n")
            for running_module in exitable_module_threads:
                running_module.exit_signal = True
            break 

        # Wait on all the threads to exit
        pool.shutdown(wait=True)


    def rcv_sensor_notification(self, message: FarmBIOSMessage):
        """
           A method for local calls to receive sensor notifications.
           :param message: The message from the wire.
        """
        # Unpack the update
        update = WaterGuardUpdate()
        update.ParseFromString(message.compute.update)
        new_rowkeys = [ key for key in update.rowKeys ]
        self.log("New row keys %s\n" % new_rowkeys)
        if len(new_rowkeys) > 1:
            top_rowkey = max([int(key) for key in new_rowkeys])
        else: # Contract with waterguard sensor to have at least one key.
            top_rowkey = int(new_rowkeys[0]) 

        # Select only the soil moisture and temperature sensors
        selectors = [] 
        for sensor, channel in self.config.sensorbox_config.items():
            if ('Moisture' in sensor) or ('Temp' in sensor):
                selectors.append(channel)

        # CSV-fy the selected channels
        channel_csv = ''
        for index, channel in enumerate(selectors):
            if index < (len(selectors)-1):
                channel_csv += channel + ','
            else:
                channel_csv += channel


        # Build the query spec
        #update_query = WaterGuardUpdate()
        #update_query.tableName = update.tableName
        query_str = "PartitionKey eq " + '\'FarmName\''
        query_str += " and RowKey eq " + '\'' + str(top_rowkey) + '\''
        self.log("Issuing query: %s\n" % query_str)

        # Get a StorageRPC with the given parameters
        storage_query_rpc = get_storage_rpc(CallType.READ,
                                            update.tableName,
                                            row_filter=query_str,
                                            selectors=channel_csv)

        # Register a call back to finish the registration and configuration
        outgoing_msg = self.dispatcher.compose_outbound(storage_query_rpc,
                                                        mod.COMPUTE,
                                                        mod.STORAGE,
                                                        watg_comp_cb.ANALYTICS)
        self.dispatcher.dispatch_message(outgoing_msg)

        return None, None


    def analytics(self, message: FarmBIOSMessage):
        """
           Run the waterguard business logic.
           :param message: The message from the wire.
        """
        # Check the status of the query sent to storage.
        response_type = message.storage.procedure.response
        if response_type == ResponseType.REQUESTED_DATA:
            # Unpack the received data
            new_data = RequestedReadData()
            new_data.ParseFromString(message.data)

            # Get the channels of moisture and temperature
            for sensor, channel in self.config.sensorbox_config.items():
                if 'Moisture' in sensor:
                    moisture_channel = channel 
                elif 'Temp' in sensor:
                    temp_channel = channel

            # This is guaranteed to return one row
            # Therefore, the moisture and temperature level assignments
            # happen only once.
            moisture_level = 0.0
            temp_level = 0.0
            for row in new_data.rows: # GenericMap
               for column in row.mapping: # key
                   if column == moisture_channel:
                       moisture_level = float(row.mapping[column])
                   elif column == temp_channel:
                       temp_level = float(row.mapping[column])

            self.log("Moisture: {}, Temp {}".format(moisture_level,
                                                   temp_level))

            # Check if moisture level is below 50 or temp > 80
            if (moisture_level < 50.0) or (temp_level > 80.0):
                self.log("Irrigation is needed\n")
                self.log("Actuation module contact needed\n")
                body = "Yo! These plants are thirsty! Irrigation Needed!"
                twilio_msg = TwilioMessage(body=body)
                actuation_msg = ActuationRPC()
                actuation_msg.procedure.call = CallType.ACTIVATE
                actuation_msg.proc_commands = twilio_msg.SerializeToString()

                outgoing_msg = get_farmbios_message(mod.ACTUATION, actuation_msg)

                self.dispatcher.send_messages([outgoing_msg],
                                              self.config.actuation_conn)

        elif response_type == ResponseType.NO_DATA:
            update = WaterGuardUpdate()
            update.ParseFromString(message.storage.store_args)
            query_str = update.querySpec.fullQueryString
            
            self.log("Storage query %s returned no data\n" % query_str)
        elif response_type == ResponseType.ERROR:
            update = WaterGuardUpdate()
            update.ParseFromString(message.storage.store_args)
            query_str = update.querySpec.fullQueryString
            
            self.log("Storage query %s returned no data\n" % query_str)
        else:
            self.log("Unknown storage response type %s\n" % response_type)

        return None, None
