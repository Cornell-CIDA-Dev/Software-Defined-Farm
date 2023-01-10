# System imports
from typing import Any, Dict, Optional


# Local imports
from sdf.config.base_config import BaseConfig
from sdf.dairymgr.base.global_defs import (SensorInfo, ZERO_TS, SIXTY_SECONDS)
from sdf.dairymgr.vendorone.milk_yield_processor import MilkYieldReader 
from sdf.dairymgr.vendortwo.feature_processor import FeatureReader
from sdf.dairymgr.vendortwo.historical_processor import HistoricalReader 
from sdf.dairymgr.vendortwo.pencap_processor import PenCapReader
from sdf.dairymgr.vendortwo.prediction_processor import PredictionReader 
from sdf.dairymgr.vendorthree.activity_processor import ActivityReader 
from sdf.dairymgr.vendorthree.hourly_rumination_processor \
                                                    import HourlyRuminationReader
from sdf.dairymgr.utils.helpers import load_snapshot


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring sensor module runs.
class DairyManagerSensorConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the starting directory for sensor
                          update search and the snapshot name. 
        """
        super().__init__(config)

        self.start_dir = config['startDir']
        self.sensors = config['sensors'].split(',')
        self.log("Sensors %s\n" % self.sensors)
        # The directories that actually contain sensor data files.
        # Some directories may contain files from more than one sensor,
        # and it is the sensor module's job to distinguish them.
        self.target_dirs = config['targetDirs'].split(',')

        # The commercial sensor vendors that dump the sensor reports
        # This is mostly for logging and tracking purposes
        self.providers = config['providers'].split(',')

        # The commercial sensor vendor names that allow mapping of sensors
        # to directories for sensors that also map directly to the directories
        # containing their reports (e.g. vendor one)
        self.vendor_one = config['vendorOne']
        self.vendor_two = config['vendorTwo']
        self.vendor_three = config['vendorThree']

        # The snapshot file to save/load (if it exists).
        self.default_snapshot = config['defaultSnapshotName']

        # Set the sleep time for the sensor module checks
        # The value should be in minutes to be multiplied by sixty seconds.
        self.sleep_time = int(config['sleepyTime']) * SIXTY_SECONDS


    def load_snapshot(self, user_snapshot_path: str = None):
        """
           Load a user-specified snapshot if one already exists.
           :param user_snapshot_path: The fully qualified file path.
        """
        if user_snapshot_path:
            self.proc_snapshot = load_snapshot(self.default_snapshot,
                                               self.target_dirs,
                                               user_snapshot_path)
        else:
            self.proc_snapshot = load_snapshot(self.default_snapshot,
                                               self.target_dirs)

    def create_reader_map(self):
        """
           Create the mapping from sensor names to their readers.
        """
        self.reader_map = {}
        for sensor_name in self.sensors:
            if sensor_name == 'pencap':
                sensor_tuple = SensorInfo(sensor_name, sensor_name, ZERO_TS)
                self.reader_map[sensor_name] = PenCapReader() 
            elif sensor_name == 'freshfeatures':
                sensor_tuple = SensorInfo(sensor_name, sensor_name, ZERO_TS)
                self.reader_map[sensor_name] = FeatureReader() 
            elif sensor_name == 'historical':
                sensor_tuple = SensorInfo(sensor_name, sensor_name, ZERO_TS)
                self.reader_map[sensor_name] = HistoricalReader()
            elif sensor_name == 'prediction':
                sensor_tuple = SensorInfo(sensor_name, sensor_name, ZERO_TS)
                self.reader_map[sensor_name] = PredictionReader()
            elif sensor_name == 'activity':
                sensor_tuple = SensorInfo(sensor_name, self.vendor_three, ZERO_TS)
                self.reader_map[sensor_name] = ActivityReader()
            elif sensor_name == 'rumination':
                sensor_tuple = SensorInfo(sensor_name, self.vendor_three, ZERO_TS)
                self.reader_map[sensor_name] = HourlyRuminationReader()
            elif sensor_name == self.vendor_one:
                sensor_tuple = SensorInfo(sensor_name, self.vendor_one, ZERO_TS)
                self.reader_map[sensor_name] = MilkYieldReader()
            else:
                print("Unknown sensor %s, exiting...\n" % sensor_name)
                exit(0)

            self.proc_snapshot.add_sensor_tuple(sensor_tuple)


# An abstract class for configuring compute module runs.
class DairyManagerComputeConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the starting directory for sensor
                          update search and the snapshot name. 
        """
        super().__init__(config)

        self.sensors = config['sensors'].split(',')
        self.log("Sensors %s\n" % self.sensors)
