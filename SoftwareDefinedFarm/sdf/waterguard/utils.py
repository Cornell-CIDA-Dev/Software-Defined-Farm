# System imports
from typing import Any, Optional


# Local packages
from sdf.waterguard.proto.waterguard_pb2 import (TableOperation,
                                                 RequestedReadData)
from sdf.farmbios.proto.storage_pb2 import StorageRPC


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


def get_storage_rpc(call: Any,
                    table_name: str,
                    row_filter: Optional[str] = None,
                    selectors: Optional[str] = None,
                    num_results: Optional[int] = None):
    """
        Construct a query message to be sent to storage.
        :param call: The storage call to make.
        :param table_name: The table to be queried. 
        :param row_filter: The partitioning string.
        :param selectors: The column filter.
        :param num_results: The max number of results to return.
        :rtype: StorageRPC
    """
    storage_msg = StorageRPC()
    storage_msg.procedure.call = call 
    query_params = TableOperation(tableName=table_name)

    if row_filter:
        query_params.filterString = row_filter

    if selectors:
        query_params.selectors = selectors 

    if num_results:
        query_params.numResults = num_results 

    storage_msg.store_args = query_params.SerializeToString()
    return storage_msg 


def unpack_rowkey_data(data: bytes):
    """
       Unpack rows received from the wire, including the top row.
       :param data: The message data to be parsed.
    """
    new_rowkeys = RequestedReadData()
    new_rowkeys.ParseFromString(data)
    new_rowkeys = [ tel.mapping['RowKey'] for tel in new_rowkeys.rows]
    max_rowkey = max([int(row_key) for row_key in new_rowkeys])

    return new_rowkeys, max_rowkey
