#from pathlib import Path
from typing import Any, Dict, List


# Local packages
from sdf.storage.base_storage import StorageModule 


# Third party packages
from boto3 import client


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A wrapper class for downloading objects from S3 buckets.
class S3Service(StorageModule):

    def __init__(self,
                 config: Any,
                 *args: Any,
                 **kwargs: Any):
        super().__init__()
        self.config = config


    def get_client(self):
        """
           Get a new client for S3 service calls.
        """
        return client('s3')


    def read(self,
             bucket_name: str,
             object_name: str,
             destinaton_file: str):
        """
           Download a blob from S3 to be saved locally.
           :param bucket_name: The bucket to read from.
           :param object_name: The object name to retrieve.
           :param destinaton_file: The file name to save the object under.
        """
        client = self.get_client()
        client.download_file(bucket_name, object_name, destinaton_file)


    def write(self,
              file_name,
              bucket_name: str,
              object_name: str=None):
        """
           Upload a blob to an S3 bucket.
           :param file_name: The path to the file to be uploaded.
           :param bucket_name: The bucket that stores the uploaded file.
           :param object_name: The object name to assign to the file in bucket.
        """
        client = self.get_client()
        status = client.upload_file(file_name, bucket_name, object_name)
        self.log("File %s successful upload status: %s\n" % (file_name,
                                                             status))
        return status
