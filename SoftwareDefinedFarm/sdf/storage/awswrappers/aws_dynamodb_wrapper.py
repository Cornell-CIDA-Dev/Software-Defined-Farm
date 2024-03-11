# System imports
#from pathlib import Path
from typing import Any, Dict, List


# Local packages
from sdf.storage.nasacloudwrappers.data_pull_typedefs import (TaskTypes, OutputTypes,
                                              SpatialProjections as Projections)
from sdf.storage.base_storage import StorageModule 
                                                         

# Third party packages
from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr 


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A Wrapper class for calling the DynamoDB geo database.
class DynamoDBService(StorageModule):

    def __init__(self,
                 config: Any,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config
        self.resource = None


    def get_resource(self):
        """
           Get a new DynamoDB resource for service calls.
        """
        return resource('dynamodb')


    def create_table(self, params: Any):
        """
           Create a new table in the database.
           :params: The parameters to pass down for table creation.
        """
        dynamodb = self.get_resource()
        table = dynamodb.create_table(params)
        # Wait until table is ready before exiting
        table.wait_until_exists()
        return table


    def get_table(self, table_name: str):
        """
           Get a table client for an existing table.
        """
        return self.get_resource().Table(table_name)


    def write(self,
              table_name: str,
              item: Any):
        """
           Put in a new item in an existing table.
           :param item: The contents of the item.
                        Valid types to be used be found at
                     https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/dynamodb.html#ref-valid-dynamodb-types
        """
        table = self.get_table(table_name)
        table.put_item(Item=item)


    def read(self,
             table_name: str,
             request: Any):
        """
           Get an item from an existing table.
           This is akin to "reading" from the database.
           :param table_name: The table to be used for the request.
           :param request: The specs for the items.
                       Valid spec can be found at https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_GetItem.html.
        """
        table = self.get_table(table_name)
        response = table.get_item(Key=request)
        return response


    def update_item(self,
                    table_name: str,
                    item: Any):
        """
           Update an existing item in a table.
           :param table_name: The table to be used for the request.
           :param item: The spec for the item to update.
        """
        table = self.get_table(table_name)
        table.update_item(item)


    def delete_item(self,
                    table_name: str,
                    item: Any):
        """
           Delete an item from an existing table.
           :param table_name: The table to be used for the request.
           :param item: The spec for the item to delete.
        """
        table = self.get_table(table_name)
        table.delete_item(item)


    def query_table(self,
                    table_name: str,
                    query_filter: Any): 
        """
           Query an existing table for the specified filter condition.
           :param table_name: The table to be used for the request.
           :param query_filter: The filtering expression to be used.
        """
        table = self.get_table(table_name)
        response = table.query(filter_exp)
        return response


    def scan_table(self,
                   table_name: str,
                   scan_filter: Any):
        """
           Scan an existing table for items with specified attributes.
           :param table_name: The table to be used for the request.
           :param scan_filter: The scanning expression to be used.
        """
        table = self.get_table(table_name)
        response = table.scan(scan_filter)
        return response
