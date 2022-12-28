# System imports
from enum import Enum
from typing import List, Union, Optional


# Local packages
from sdf.storage.base_storage import StorageModule 


# Third party packages
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class TableOpStatus(Enum):
    CREATE_SUCCESS = 1
    SKIP_CREATE = 2
    DELETE_SUCCESS = 3
    SKIP_DELETE = 4


# @brief: A wrapper class for operations to the Azure Table service.
class AzureTableService(StorageModule):


    def __init__(self, connection_string: str):
        """
           :param connection_string: The storage account pointer.
        """
        super().__init__()
        self.connection_string = connection_string


    def create_table(self, table_name: str):
        """
            Create a table to push data to Azure
            :param table_name: Self explanatory.
        """
        table_handle = TableService(connection_string=self.connection_string)

        # First check whether the table exists before creation attempt.
        if table_handle.exists(table_name):
            self.log("Table %s already exists! Skipping operation\n" % table_name)
            return TableOpStatus.SKIP_CREATE
        else:
            self.log("Creating %s table\n" % table_name)
            table_handle.create_table(table_name)
            return TableOpStatus.CREATE_SUCCESS


    def delete_table(self, table_name: str):
        """
            Delete a table from Azure resource
            :param table_name: Self explanatory.
        """
        table_handle = TableService(connection_string=self.connection_string)

        # First check whether the table exists before deletion attempt.
        if table_handle.exists(table_name):
            self.log("Deleting %s table\n" % table_name)
            table_handle.delete_table(table_name)
            return TableOpStatus.DELETE_SUCCESS
        else:
            self.log("Table %s doesn't exist, Skipping deletion operation\n" % \
                   table_name)
            return TableOpStatus.SKIP_DELETE


    def write_table(self,
                    table_name: str,
                    json_data: Union[dict, Entity]):
        """
           Push sensor data received from service bus to an established Azure table.
           :param table_name: Self explanatory.
           :parama json_data: A JSON object.
        """
        table_handle = TableService(connection_string=self.connection_string)
        table_handle.insert_or_replace_entity(table_name, json_data)


    def write_table_batch(self,
                          table_name: str,
                          entities: List[Entity]):
        """
           Push sensor data received from service bus to an established Azure table.
           :param table_name: Self explanatory.
           :parama entities: The list of Entity objects to push.
        """
        table_handle = TableService(connection_string=self.connection_string)
        with table_handle.batch(table_name) as batch:
            for entity in entities:
                batch.insert_entity(entity)


    def read_table(self,
                   table_name: str,
                   filter_string: str,
                   selectors: Optional[str],
                   num_results: Optional[int] = None):
        """
            Query existing data in the table.
            :param table_name: Self explanatory.
            :param filter_string: The column filter condition.
            :param selectors: A csv with the columns to select in results.
            :param num_results: The max number of entries to return.
        """
        table_handle = TableService(connection_string=self.connection_string)
        if selectors:
            return table_handle.query_entities(table_name,
                                               filter=filter_string,
                                               select=selectors,
                                               num_results=num_results)
        else:
             return table_handle.query_entities(table_name,
                                                filter=filter_string,
                                                num_results=num_results)
