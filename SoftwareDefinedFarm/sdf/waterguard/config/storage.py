# System imports
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# A class for configuring the WaterGuard storage module.
class WaterGuardStorageConfig(BaseConfig):

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

        self.table_conn_string = config['tableConnectionString']

        # Configure all the module IP addresses (if any)
        self.storage_host = config['storageHost']
        self.storage_port = int(config['storagePort'])


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher

