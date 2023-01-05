# System imports
from enum import Enum
from typing import Any


# Local packages
from sdf.storage.base_storage import StorageModule 


# Third party packages
from azure.storage.blob import BlobServiceClient


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class BlobOpStatus(Enum):
    CREATE_CONTAINER_SUCCESS = 1
    CREATE_CONTAINER_FAILURE = 2
    DELETE_CONTAINER_SUCCESS = 3
    DELETE_CONTAINER_FAILURE = 4
    UPLOAD_BLOB_SUCCESS = 5
    UPLOAD_BLOB_FAILURE = 6
    GET_BLOB_FAILURE = 7 
    DELETE_BLOB_SUCCESS = 8
    DELETE_BLOB_FAILURE = 9


# @brief: A wrapper class for operations to the Azure Blob service.
class AzureBlobService(StorageModule):


    def __init__(self, connection_string: str):
        """
           :param connection_string: The storage account pointer.
        """
        super().__init__()
        self.connection_string = connection_string


    def create_container(self, container_name: str):
        """
           Create the blob container in the storage account.
           :param container_name: The container's unique name.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
                                                        self.connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Catch the exception if the operation fails.
        try:
            container_client.create_container()
            return BlobOpStatus.CREATE_CONTAINER_SUCCESS
        except Exception as ex:
            self.log("Ex: %s -> Container creation for %s failed\n" % (ex,
                                                              container_name))
            return BlobOpStatus.CREATE_CONTAINER_FAILURE


    def delete_container(self, container_name: str):
        """
           Delete the blob container in the storage account.
           :param container_name: The container's unique name.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
                                                        self.connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Catch the exception if the operation fails.
        try:
            container_client.delete_container()
            return BlobOpStatus.DELETE_CONTAINER_SUCCESS
        except Exception as ex:
            self.log("Ex: %s -> Container deletion for %s failed\n" % (ex,
                                                              container_name))
            return BlobOpStatus.DELETE_CONTAINER_FAILURE


    def write(self, container_name: str,
              blob_name: str,
              data: Any):
        """
           Upload a blob to the given container..
           :param container_name: The container's unique name.
           :param blob_name: The name to be used for uploading the blob.
           :param data: The file/binary data to upload.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
                                                        self.connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Catch the exception if the operation fails.
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, blob_type="BlockBlob")
            return BlobOpStatus.UPLOAD_BLOB_SUCCESS
        except Exception as ex:
            self.log("Ex: %s -> Upload for %s in %s container failed\n" %  (ex,
                                                                     blob_name,
                                                                container_name))
            return BlobOpStatus.UPLOAD_BLOB_FAILURE


    def read(self,
             container_name: str,
             blob_name: str):
        """
           Download a blob to the local filesystem.
           :param container_name: The container's unique name.
           :param blob_name: The name to be used for uploading the blob.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
                                                        self.connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Catch the exception if the operation fails.
        try:
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.download_blob().readall()
        except Exception as ex:
            self.log("Ex: %s -> Download for %s in %s container failed\n" % (ex,
                                                                      blob_name,
                                                                container_name))
            return BlobOpStatus.GET_BLOB_FAILURE


    def delete_blob(self,
                    container_name: str,
                    blob_name: str):
        """
           Download a blob to the local filesystem.
           :param container_name: The container's unique name.
           :param blob_name: The name to be used for uploading the blob.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
                                                        self.connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Catch the exception if the operation fails.
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            return BlobOpStatus.DELETE_BLOB_SUCCESS
        except Exception as ex:
            self.log("Ex: %s -> Deletion for %s in %s container failed\n" % (ex,
                                                                      blob_name,
                                                                container_name))
            return BlobOpStatus.DELETE_BLOB_FAILURE
