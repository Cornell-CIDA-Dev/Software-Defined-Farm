# System imports
from queue import Queue
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.waterguard.utils import get_storage_rpc, unpack_rowkey_data
from sdf.waterguard.callback_enum_defs import WaterGuardConfigCallBacks as watg_conf_cb
from sdf.waterguard.proto.waterguard_pb2 import (RequestedReadData, WriteData,
                                                WriteType, WriteLocation)


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring sensor module runs.
class WaterGuardSensorConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the storage connection string
                          and the co-location status with the other 
                          modules.
        """
        super().__init__(config)

        self.watch_table = config['watchTable']

        # Init sensor box identity
        self.sensorbox_id = config['sensorboxId'] 
        self.sensorbox_table = "AgSensorBoxData" + self.sensorbox_id
        self.config_table = "AgSensorBoxConfig" + self.sensorbox_id

        # Configure all the module IP addresses (if any)
        self.sensor_host = config['sensorHost']
        self.sensor_port = int(config['sensorPort'])
        self.storage_host = config['storageHost']
        self.storage_port = int(config['storagePort'])

        # Set the sleep time for the sensor module checks
        self.sleep_time = int(config['sleepyTime'])

        # The variable to check watch table config status
        self.watch_table_partition = None


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def handle_callback(self,
                        message: FarmBIOSMessage,
                        callback_func: watg_conf_cb,
                        **kwargs):
       """
           Call the appropriate handler for config call backs.
           :param message: The message with the response for the call back.
           :param callback_func: The local function to pass the message to.
       """
       self.log("HANDLING CALLBACK FOR: %s\n" % callback_func.name)
       if callback_func == watg_conf_cb.FINISH_SENSORBOX_CONFIG:
           return self.finish_sensorbox_config(message)
       elif callback_func == watg_conf_cb.PROCESS_WATCHTABLE_PRESENCE:
           return self.process_watch_table_presence(message)
       elif callback_func == watg_conf_cb.INSERT_LATEST_ROWKEY:
           return self.insert_latest_rowkey(message)
       else:
           self.log("Unknown call back %s\n" % callback_func, WARNING)
           return None, None


    def get_sbdata_config(self):
        """
           Retrieve the list of sensor box ports that are activated.
        """
        # Query the remote configuration
        row_filter_string = "PartitionKey eq " + '\'Seeed\''
        row_filter_string += " and Enabled"
        selectors = 'Channel,FriendlyName'
        query_rpc = get_storage_rpc(CallType.READ,
                                    self.config_table,
                                    row_filter=row_filter_string, 
                                    selectors=selectors)

        # Register a call back to finish the configuration
        outgoing_msg= self.dispatcher.compose_outbound(query_rpc,
                                                       mod.CONFIG,
                                                       mod.STORAGE,
                                          watg_conf_cb.FINISH_SENSORBOX_CONFIG)

        self.dispatcher.dispatch_message(outgoing_msg)


    def finish_sensorbox_config(self,  
                                message: FarmBIOSMessage,
                                **kwargs):
        """
           A method to finish the sensor box configuration from storage.
           :param message: The message returned by the storage module.
        """
        config_records = RequestedReadData()
        config_records.ParseFromString(message.data)

        self.sensorbox_config = {}
        for row in config_records.rows:
            channel = row.mapping['Channel']
            friendly_name = row.mapping['FriendlyName']
            self.sensorbox_config[friendly_name] = 'CompChannel' + channel

        self.log("SensorBox Config Complete -> %s\n" % self.sensorbox_config)

        return None, None


    def get_watch_table_presence(self):
        """
           Check if a partition exists for the sensor box in the watch table.
           The check happens by getting the top 1 result for the partition
           which matches to the sensor box's data table name.
        """
        # Query the watch table for a partition belonging to the sensor box 
        row_filter_string = "PartitionKey eq " + '\'' + self.sensorbox_table
        row_filter_string += '\''
        selectors = 'RowKey'
        num_results = 1
        query_rpc = get_storage_rpc(CallType.READ,
                                    self.watch_table,
                                    row_filter=row_filter_string, 
                                    selectors=selectors,
                                    num_results=num_results)


        # Register a call back to process the table presence 
        outgoing_msg= self.dispatcher.compose_outbound(query_rpc,
                                                       mod.CONFIG,
                                                       mod.STORAGE,
                                             watg_conf_cb.PROCESS_WATCHTABLE_PRESENCE)

        self.dispatcher.dispatch_message(outgoing_msg)


    def process_watch_table_presence(self, message: FarmBIOSMessage):
        """
           Add the latest row key for the sensor box's data table if there is
           no partition for it in the watch table.
           Otherwise, the call back process ends here.
        """
        # Check if there is data associated with the sensor box
        response_type = message.storage.procedure.response
        if response_type == ResponseType.REQUESTED_DATA:
            self.log("Partition for Sensor box %s exists in watch table!\n" \
                     % self.sensorbox_id)

            # The watch table config check is done
            self.watch_table_partition = True

        elif response_type == ResponseType.NO_DATA:
            # Query the top row key in sensor box's data table
            row_filter_string = "PartitionKey eq " +  '\'FarmName\''
            selectors = 'RowKey'
            query_rpc = get_storage_rpc(CallType.READ,
                                        self.sensorbox_table,
                                        row_filter=row_filter_string, 
                                        selectors=selectors)

            # Register a call back to process the table presence 
            outgoing_msg= self.dispatcher.compose_outbound(query_rpc,
                                                           mod.CONFIG,
                                                           mod.STORAGE,
                                             watg_conf_cb.INSERT_LATEST_ROWKEY)
            self.dispatcher.dispatch_message(outgoing_msg)
        else:
            self.log("Partition storage presence query for %s errored!\n" \
                     % self.sensorbox_id)
        return None, None


    def insert_latest_rowkey(self, message: FarmBIOSMessage):
        """
           Finish the call back process started by getting the presence of
           a partition for the sensor box's data table in the watch table.
           The last step of the config is to add the current top rowkey
           as the latest one before starting the sensor module.
           :param message: The message received from the wire.
        """
        # Check if there is new data
        response_type = message.storage.procedure.response
        if response_type == ResponseType.REQUESTED_DATA:

            # Unpack the row keys that are greater than the latest one
            new_rowkeys, max_rowkey = unpack_rowkey_data(message.data)

            ## Update the latest row key from watch table.
            self.log("Number of results %s" % len(new_rowkeys))

            # Create a new "latest" row key for watch table.
            updated_triggers = WriteData()
            updated_triggers.writeType = WriteType.REGULAR_WRITE
            updated_triggers.location = WriteLocation.WATCH_TABLE
            new_trigger_row = updated_triggers.rows.add()
            new_trigger_row.mapping['PartitionKey'] = self.sensorbox_table
            new_trigger_row.mapping['RowKey'] = str(max_rowkey)
            new_trigger_row.mapping['outdated'] = 'latest'

            write_rpc = get_storage_rpc(CallType.WRITE,
                                        self.watch_table)
            serialized_data = updated_triggers.SerializeToString()
            outgoing_msg = get_farmbios_message(mod.STORAGE, write_rpc,
                                                data=serialized_data)

            self.dispatcher.send_messages([outgoing_msg], self.storage_conn)

            # The watch table config check is done
            self.watch_table_partition = True
        elif response_type == ResponseType.NO_DATA:
            self.log("No records for Sensor box %s exist?? Investigate!\n" \
                     % self.sensorbox_id)
        else:
            self.log("Query for Sensor box %s' records errored\n" \
                     % self.sensorbox_id)
        return None, None
