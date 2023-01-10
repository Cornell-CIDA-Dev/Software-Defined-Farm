from pickle import dump
from time import sleep
from typing import List

from sdf.dairymgr.base.global_defs import SensorInfo
from sdf.utils.threaded_universal_base_class import ThreadedUniversalBase

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# A class for saving structs about the state of filesystem. 
class Snapshot(ThreadedUniversalBase):

    def __init__(self,
                 interval: int,
                 snapshot_file_path: str,
                 target_dirs: List
                 ):
        """
           Keep track of the current snapshot of the farm PC.
           Dirty bits determines if/when to backup the struct again.
           :param interval: An integer.
           :param snapshot_file_path: A string.
           :param target_dirs: The list of directories to search.
        """
        self.snapshot_struct = {}
        self.snapshot_interval = interval
        self.snapshot_file_path = snapshot_file_path
        self.target_dirs = target_dirs
        self.dirty_bit = False
        super().__init__()


    def add_sensor_tuple(self, sensor_tuple : SensorInfo):
        """
           Add a new processor to the snapshot struct.
           This leaves room for future expansion based on the guiding
           principles of the Software-Defined Farm.
           :param sensor_tuple: TBD by the struct user.
        """
        sensor_name = sensor_tuple.name
        if sensor_name in self.snapshot_struct:
            print("%s SensorInfo already exists!\n" % sensor_name)
            return False

        self.snapshot_struct[sensor_name] = sensor_tuple
                                             
        return True


    def monitor_snapshot_struct(self):
        """
           Check if the dirty bit has been changed by the general processor.
        """
        while not(self.exit_signal):
            if self.dirty_bit:
                with open(self.snapshot_file_path, 'wb') as snapshot_fd:
                    # Dump a new copy of the snapshot object.
                    print("Dumping snapshot copy: %s\n" % self.snapshot_file_path)
                    dump(self, snapshot_fd)
                self.dirty_bit = False

            # Sleep for the user specified interval
            sleep(self.snapshot_interval)

            # Upon wake up, check snapshot needs before exiting.
            if (self.dirty_bit == True) and (self.exit_signal == True):
                with open(self.snapshot_file_path, 'wb') as snapshot_fd:
                    # Dump a new copy of the snapshot object.
                    print("Dumping snapshot before exit: %s\n" % self.snapshot_file_path)
                    self.dirty_bit = False
                    dump(self, snapshot_fd)


    def update_latest_ts(self,
                         sensor_name: str,
                         timestamp: float):
        """
           Update the latest timestamp for a log entries of a sensor.
           :param sensor_name: The sensor whose records to update.
           :param timestamp: A float.
        """
        latest_sensor_ts = self.snapshot_struct[sensor_name].latest_ts
        print("%s's latest ts %s\n" % (sensor_name, latest_sensor_ts))
        print("New timestamp %s" % timestamp)
        if timestamp > latest_sensor_ts:
            self.snapshot_struct[sensor_name].latest_ts = timestamp
            print("Updated %s sensor's latest ts to %s\n" % (sensor_name, timestamp))
