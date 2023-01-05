# System imports
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import time, sleep
from typing import Any
from logging import WARNING


# Local packages
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.sensor_pb2 import SensorRPC
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.waterguard.callback_enum_defs import \
                                      WaterGuardSensorCallBacks as watg_sens_cb
from sdf.sensors.base_sensor import SensorModule
from sdf.utils.user_input import create_request
from sdf.waterguard.config.sensor import WaterGuardSensorConfig
from sdf.waterguard.proto.waterguard_pb2 import (WaterGuardUpdate,
                                                 RequestedReadData,
                                                 WriteData, WriteType,
                                                 WriteLocation)
from sdf.waterguard.utils import get_storage_rpc, unpack_rowkey_data


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

SIXTY_SECONDS = 60

# An abstract class for operating on FarmBeats sensor box data.
class WaterGuardSensor(SensorModule):

    def __init__(self,
                 config: WaterGuardSensorConfig,
                 *args: Any,
                 **kwargs: Any):
        self.config = config
        self.storage_conn = self.config.storage_conn
        self.sensorbox_table = self.config.sensorbox_table
        super().__init__()


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def handle_callback(self,
                        message: FarmBIOSMessage,
                        callback_func: watg_sens_cb,
                        **kwargs):
       """
           Call the appropriate handler for sensor module call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       self.log("HANDLING CALLBACK FOR: %s\n" % callback_func.name)
       if callback_func == watg_sens_cb.SET_TOP_ROW_KEY:
           return self.set_top_rowkey(message)
       elif callback_func == watg_sens_cb.QUERY_NEW_ROWKEYS:
           return self.query_new_rowkeys(message)
       elif callback_func == watg_sens_cb.PROCESS_READ_RESULTS:
           return self.process_read_results(message)
       else:
           self.log("Unknown call back %s\n" % callback_func, WARNING)
           return None, None


    def check_sensor_update(self):
        """
           Check if an update to the top row key (i.e. sensor update)
           is needed 
        """
        while True:
            # Pull the latest rowkey from watch table.
            row_filter_string = "PartitionKey eq " + '\'' + self.sensorbox_table
            row_filter_string += '\''
            row_filter_string += " and outdated eq " + '\'latest\''
            selector = 'RowKey'
            query_rpc = get_storage_rpc(CallType.READ,
                                        self.config.watch_table,
                                        row_filter=row_filter_string,
                                        selectors=selector)

            # Register a call back to finish getting/setting the top row key
            outgoing_msg= self.dispatcher.compose_outbound(query_rpc,
                                                           mod.SENSOR,
                                                          mod.STORAGE,
                                                  watg_sens_cb.SET_TOP_ROW_KEY)

            self.dispatcher.dispatch_message(outgoing_msg)

            # Sleep as the call backs are handled by the network controller.
            sleep_duration = self.config.sleep_time * SIXTY_SECONDS
            self.log("Sleeping for %s seconds...\n" % sleep_duration)
            sleep(sleep_duration)

            # Check if there's an instruction to exit upon waking up.
            if self.exit_signal:
                self.log("WaterGuard sensor check thread registered exit signal")
                return

    def run(self,
           dispatcher: Any):
        """
           Start the threads for the different functions.
           Note that we're passing the dispatcher for now, but it may not
           be useful in the future.
           :param dispatcher: The dispatcher for incoming/outgoing messages.
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
        exitable_module_threads.append(net_ctrl)

        # Wait for the watch table config before starting run
        while self.config.watch_table_partition == None:
            print("Waiting 5 secs for watch table config..\n")
            sleep(5) 

        # Run a thread to send time updates.
        check_future = pool.submit(self.check_sensor_update)
        check_future.add_done_callback(self.check_on_threads)

        # Await user exit request.
        while True:
            request = create_request()
            print("Received a signal to exit, releasing resources\n")
            for running_module in exitable_module_threads:
                running_module.exit_signal = True
            break 

        # Wait on all the threads to exit
        pool.shutdown(wait=True)


    def set_top_rowkey(self, message: FarmBIOSMessage):
        """
           Set the top row key for the module's sensor box
           :param message: The message from the wire.
        """
        requested_data = RequestedReadData()
        requested_data.ParseFromString(message.data)
        # There is only one result, so this may be unnecessary
        for index, row in enumerate(requested_data.rows):
            if index == 0:
                self.trigger_rowkey = str(row.mapping['RowKey'])
            self.log("Last trigger key %s\n" % self.trigger_rowkey)

        # Create query row string and selectors for greater row keys
        row_filter_string = "RowKey gt " + '\'' + self.trigger_rowkey + '\''
        selector = 'RowKey'
        query_rpc = get_storage_rpc(CallType.READ,
                                    self.sensorbox_table,
                                    row_filter=row_filter_string,
                                    selectors=selector)

        # Register a call back to query the data on any new rowkeys 
        outgoing_msg= self.dispatcher.compose_outbound(query_rpc,
                                                       mod.SENSOR,
                                                       mod.STORAGE,
                                             watg_sens_cb.QUERY_NEW_ROWKEYS)

        self.dispatcher.dispatch_message(outgoing_msg)
        return None, None


    def query_new_rowkeys(self, message: FarmBIOSMessage):
        """
           Query the data from new row keys.
           :param message: The message from the wire.
        """
        # Check if there is new data
        response_type = message.storage.procedure.response
        if response_type == ResponseType.REQUESTED_DATA:

            # Unpack the row keys that are greater than the latest one
            new_rowkeys, max_rowkey = unpack_rowkey_data(message.data)

            # Update the latest row key from watch table.
            self.log("Number of results %s" % len(new_rowkeys))
            self.log("Results %s\n" % new_rowkeys)

            # Update the old "latest" row key from watch table.
            updated_triggers = WriteData()
            updated_triggers.writeType = WriteType.REGULAR_WRITE
            updated_triggers.location = WriteLocation.WATCH_TABLE
            old_trigger_row = updated_triggers.rows.add()
            old_trigger_row.mapping['PartitionKey'] = self.sensorbox_table
            old_trigger_row.mapping['RowKey'] = self.trigger_rowkey
            current_time = datetime.utcfromtimestamp(time())
            old_trigger_row.mapping['outdated'] = str(current_time)

            # Create a new "latest" row key for watch table.
            new_trigger_row = updated_triggers.rows.add()
            new_trigger_row.mapping['PartitionKey'] = self.sensorbox_table
            new_trigger_row.mapping['RowKey'] = str(max_rowkey)
            new_trigger_row.mapping['outdated'] = 'latest'

            write_rpc = get_storage_rpc(CallType.WRITE,
                                        self.config.watch_table)

            ## Register a call back to query the data on any new rowkeys 
            #callback_tuple = get_callback_tuple(None, mod.STORAGE, mod.SENSOR,
            #                                     watg_sens_cb.FINISH_CONFIG)
            #self.dispatcher.register_callback(callback_tuple)

            # Get the farmbios message and set the callback id
            serialized_data = updated_triggers.SerializeToString()
            outgoing_msg = get_farmbios_message(mod.STORAGE, write_rpc,
                                                data=serialized_data)

            self.dispatcher.send_messages([outgoing_msg], self.storage_conn)

            # Next call: On successful write, notify the observers

            # Create the update with table, new keys and possible selectors.
            update = WaterGuardUpdate()
            update.tableName = self.sensorbox_table
            update.rowKeys.extend(new_rowkeys)
            for sensor, channel in self.config.sensorbox_config.items():
                update.possibleSensors.mapping[sensor] = channel

            compute_msg = ComputeRPC()
            compute_msg.procedure.call = CallType.RCV_SENSOR_NOTIFICATION
            compute_msg.update = update.SerializeToString()

            # Serialize message and notify observers of the new row keys
            farmbios_msg = get_farmbios_message(mod.COMPUTE, compute_msg)
            self.set_changed()
            self.notify(farmbios_msg)
        elif response_type == ResponseType.NO_DATA:
            self.log("No new rows beyond %s\n" % self.trigger_rowkey) 
        else:
            self.log("Possible storage query error")

        return None, None


    def register(self,
                 message: FarmBIOSMessage,
                 observer: Any):
        """
           Override the super's register to insert waterguard specific return.
           :param observer: The peer to register
        """
        # Register the observer
        super().register(observer)
        sensor_msg = SensorRPC()
        sensor_msg.procedure.response = ResponseType.REGISTER_SUCCESS

        # Compose the configuration update to be sent to them.
        # This allows not having to send the config every time
        # new rows are added to the table
        update = WaterGuardUpdate()
        update.tableName = self.sensorbox_table
        for sensor, channel in self.config.sensorbox_config.items():
            update.possibleSensors.mapping[sensor] = channel
        sensor_msg.update = update.SerializeToString()

        # Compose the FarmBIOS message.
        # Registration calls are assumed to always come with callback IDs.
        farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                            metadata=sensor_msg,
                                       callback_id=message.callback.identifier,
                                            is_final_response=True)

        # No callbacks to register with dispatcher for incoming register calls.
        return [farmbios_msg], None


    def process_read_results(self, message: FarmBIOSMessage):
        """
           Process the results from a storage call back to read
           The compute module is likely the one that called the original read.
        """
        # Unpack the response
        response_meta = message.storage
        response_type = response_meta.procedure.response

        # Create the update and prepare the response
        sensor_msg = SensorRPC()
        serialized_data = None
        farmbios_msg = None

        if response_type == ResponseType.REQUESTED_DATA:
           sensor_msg.procedure.response = ResponseType.REQUESTED_DATA
           farmbios_msg = get_farmbios_message(mod.SENSOR, sensor_msg,
                                               data=message.data) 
        elif response_type == ResponseType.NO_DATA:
           sensor_msg.procedure.response = ResponseType.NO_DATA
           farmbios_msg = get_farmbios_message(mod.SENSOR, sensor_msg) 
        elif response_type == ResponseType.ERROR:
           sensor_msg.procedure.response = ResponseType.ERROR
           farmbios_msg = get_farmbios_message(mod.SENSOR, sensor_msg) 
        else:
           self.log("Unknown read response type %s. Ignoring" % response_type)

        return [farmbios_msg], None
