# System imports
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from random import randint
from time import time
from typing import Any, Optional


# Local imports
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.storage_pb2 import StorageRPC 
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.storage.azurewrappers.azure_table_service import AzureTableService
from sdf.utils.user_input import create_request
from sdf.waterguard.proto.waterguard_pb2 import (RequestedReadData,
                                                 TableOperation,
                                                 WaterGuardUpdate,
                                                 WriteData,
                                                 WriteType,
                                                 WriteLocation)
from sdf.waterguard.config.storage import WaterGuardStorageConfig


# Third party package imports
from azure.cosmosdb.table.models import Entity


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class WaterGuardStorage(AzureTableService):

    def __init__(self,
                 config: WaterGuardStorageConfig,
                 location: Optional[Any] = None,
                 *args: Any,
                 **kwargs: Any):
        """
           :param conn_string: The unique address for the storage account.
        """
        self.config = config
        super().__init__(config.table_conn_string)


    def run(self, dispatcher: Any):
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
        # Note: The WaterGuard storage module currently has no
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
    

    def read(self, message: FarmBIOSMessage):
        """ Read from a table.
            :param message: The incoming message.
        """
        # Unpack the arguments
        store_args = message.storage.store_args
        specs = TableOperation()
        specs.ParseFromString(store_args)
        table_name = specs.tableName
        filter_string = specs.filterString
        selectors = specs.selectors
        num_results = specs.numResults
        
        query_string = "READ Table: {}, Filter: {}, Select : {}".format(
                          table_name, filter_string, selectors)
        if num_results:
            query_string += "Num Results: {}".format(str(num_results))

        self.log(query_string)


        results = None
        if selectors and num_results:
            results = self.read_table(table_name, filter_string,
                                      selectors=selectors,
                                      num_results=num_results).__iter__()
        elif selectors and not(num_results):
            results = self.read_table(table_name, filter_string,
                                      selectors=selectors).__iter__()
        else:
            results = self.read_table(table_name, filter_string).__iter__()

        ## Compose the storage result
        storage_msg = StorageRPC()
        serialized_data = None
        farmbios_msg = None

        # Unpack the results to check the iterator's length
        results = [ result for result in results ]

        if len(results) > 0:
            storage_msg.procedure.response = ResponseType.REQUESTED_DATA
            requested_data = RequestedReadData()
            unpacked_selectors = selectors.split(',')

            for record in results:
                row = requested_data.rows.add()
                for column_name in unpacked_selectors:

                    # Always unpack to str, caller will convert back
                    value = record[column_name]
                    if (isinstance(value, float)):
                        value = str(value)

                    if not(isinstance(value, str)):
                        value = str(record[column_name].value)

                    row.mapping[column_name] = value

            # Serialize the data to go in the message.
            serialized_data = requested_data.SerializeToString()
        elif len(results) == 0:
            self.log("No data found for read query %s\n" % query_string)
            storage_msg.procedure.response = ResponseType.NO_DATA
            update = WaterGuardUpdate()
            update.querySpec.fullQueryString = query_string
            storage_msg.store_args = update.SerializeToString()
        else:
            self.log("Query %s errored \n" % query_string)
            storage_msg.procedure.response = ResponseType.ERROR
            update = WaterGuardUpdate()
            update.querySpec.fullQueryString = query_string
            storage_msg.store_args = update.SerializeToString()

        # Check and, if any, initialize the callback ID
        # This is useful for the module that calls this storage module
        # to know where to resume execution from.
        callback_id = None
        if message.callback.identifier != None:
            callback_id = message.callback.identifier

        if serialized_data: 
            farmbios_msg = get_farmbios_message(msg_type=mod.STORAGE,
                                                metadata=storage_msg,
                                                data=serialized_data,
                                                callback_id=callback_id,
                                               is_final_response=True)
        else:
            farmbios_msg = get_farmbios_message(msg_type=mod.STORAGE,
                                                metadata=storage_msg,
                                                callback_id=callback_id,
                                                is_final_response=True)

        return [farmbios_msg], None


    def write(self, message: FarmBIOSMessage):
        """ Write/update data to/in a table.
            :param message: The incoming message. 
        """
        # Unpack the arguments
        store_args = message.storage.store_args
        data = message.data
        specs = TableOperation()
        specs.ParseFromString(store_args)
        table_name = specs.tableName

        write_data = WriteData()
        write_data.ParseFromString(data)

        # Log the writing location
        location = write_data.location
        if location == WriteLocation.WATCH_TABLE:
            self.log("Writing to watch table %s\n" % table_name)
        elif location == WriteLocation.SENSOR_BOX_TABLE:
            self.log("Writing to sensor box table %s\n" % table_name)
        else:
            self.log("Unknown write location %s\n" % location)

        if write_data.writeType == WriteType.REGULAR_WRITE:
            for inbound_entity in write_data.rows:
                ent = Entity()
                ent.PartitionKey = inbound_entity.mapping['PartitionKey']
                ent.RowKey = inbound_entity.mapping['RowKey']
                ent.outdated = inbound_entity.mapping['outdated']
                self.write_table(table_name, ent)
        elif write_data.writeType == WriteType.BATCH_WRITE:
            entities = []
            for inbound_entity in write_data.rows:
                ent = Entity()
                ent.PartitionKey = inbound_entity.mapping['PartitionKey']
                ent.RowKey = inbound_entity.mapping['RowKey']
                ent.outdated = inbound_entity.mapping['outdated']
                entities.append(ent)
            self.write_table_batch(table_name, entities) 
        else:
            self.log("Unknown write type %s\n" % write_data.writeType)

        # Check and, if any, initialize the callback ID
        # This is useful for the module that calls this storage module
        # to know where to resume execution from.
        callback_id = None
        if message.callback.identifier != None:
            callback_id = message.callback.identifier

        ## Compose the storage result
        storage_msg = StorageRPC()
        storage_msg.procedure.response = ResponseType.SUCCESS
        farmbios_msg = get_farmbios_message(msg_type=mod.STORAGE,
                                            metadata=storage_msg,
                                            callback_id=callback_id,
                                            is_final_response=True)
        return [farmbios_msg], None
