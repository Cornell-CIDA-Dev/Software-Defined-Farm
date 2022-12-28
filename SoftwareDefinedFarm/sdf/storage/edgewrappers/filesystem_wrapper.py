# System imports
from enum import Enum


# Local packages
from sdf.storage.base_storage import StorageModule 


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class FileOpStatus(Enum):
    READ_SUCCESS = 1
    FILE_NOT_FOUND = 2
    WRITE_SUCCESS = 3
    WRITE_FAILURE = 4


# @brief: A wrapper class for operations to the file system.
class FileSystemService(StorageModule):


    def __init__(self):
        super().__init__()


    def read_file(self, path: str):
        """
           Read all the contents from a local file. 
           :param path: Self explanatory.
        """
        try:
            with open(path, "rb") as fd:
                data = fd.read()
                return FileOpStatus.READ_SUCCESS, data
        except FileNotFoundError as fnf:
            self.log("File %s not found\n" % path)
            return FileOpStatus.FILE_NOT_FOUND, None


    def write_file(self,
                   path: str,
                   data: bytes):
        """
           Write contents to a local file. 
           :param path: Self explanatory.
           :param data: The (bytes) content to write.
        """
        try:
            with open(path, "wb") as fd:
                fd.write(data)
                return FileOpStatus.WRITE_SUCCESS
        except FileNotFoundError as fnf:
            self.log("File %s not found\n" % path)
            return FileOpStatus.WRITE_FAILURE
