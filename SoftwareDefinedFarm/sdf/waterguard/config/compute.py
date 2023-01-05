# System imports
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring the compute module.
class WaterGuardComputeConfig(BaseConfig):

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
        self.watch_table = config['watchTable']

        # Init sensor box identity
        self.sensorbox_id = config['sensorboxId'] 
        self.sensorbox_table = "AgSensorBoxData" + self.sensorbox_id
        self.config_table = "AgSensorBoxConfig" + self.sensorbox_id

        # Configure all the module IP addresses (if any)
        self.compute_host = config['computeHost']
        self.compute_port = int(config['computePort'])
        self.sensor_host = config['sensorHost']
        self.sensor_port = int(config['sensorPort'])
        self.storage_host = config['storageHost']
        self.storage_port = int(config['storagePort'])
        self.actuation_host = config['actuationHost']
        self.actuation_port = int(config['actuationPort'])

        # The variable to check watch table config status
        self.watch_table_partition = None
