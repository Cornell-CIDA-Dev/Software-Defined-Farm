# System packages
from os import scandir, walk
from pathlib import Path
from time import sleep
from typing import List, Any


# Local packages
from sdf.dairymgr.base.global_defs import SensorUpdate
from sdf.dairymgr.dairymgr_config import DairyManagerSensorConfig
from sdf.dairymgr.proto.generated.update_pb2 import DairyMgrSensorUpdate
from sdf.dairymgr.utils.helpers import process_dairymgr_updates
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.sensor_pb2 import SensorRPC
from sdf.farmbios.proto.shared_pb2 import ResponseType
from sdf.helper_typedefs import Modules as mod
from sdf.sensors.base_sensor import SensorModule


# Third party packages


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# A class for monitoring new sensor updates.
class DairyManagerSensor(SensorModule):


    def __init__(self,
                 config: DairyManagerSensorConfig,
                 *args: Any,
                 **kwargs: Any):
        """
           Process new sensor data on any given date.
        """
        self.config = config
        self.proc_snapshot = self.config.proc_snapshot 
        self.net_ctrl = self.config.net_ctrl
        self.periodic_check_interval = self.config.sleep_time 
        self.reader_map = self.config.reader_map
        super().__init__()


    def set_dispatcher(self, dispatcher: Any):
        """
           Set the dispatcher that sends requests and responses to peer modules.
           :param dispatcher: Self-explanatory.
        """
        self.dispatcher = dispatcher


    def register(self,
                 message: FarmBIOSMessage,
                 observer: Any):
        """
           Override the base class' register to insert dairymgr specific return.
           :param observer: The peer to register
        """
        # Register the observer
        super().register(observer)

        # Compose the registration response
        sensor_msg = SensorRPC()
        sensor_msg.procedure.response = ResponseType.REGISTER_SUCCESS

        # Future possibility: return the list of sensors whose updates
        # will be coming, and send this as a list of DairyMgrSensorUpdates.


        # Compose the FarmBIOS message.
        # Registration calls are assumed to always come with callback IDs.
        farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                            metadata=sensor_msg,
                                       callback_id=message.callback.identifier,
                                            is_final_response=True)

        # No callbacks to register with dispatcher for incoming register calls.
        return [farmbios_msg], None


    def are_provider_dirs_present(self,
                                  starting_dir: str,
                                  directories: List):
        """
           Check that given directories exist before starting checks.
           :param starting_dir: The path where to look for provider dirs.
           :param directories: The providers' directory names.
        """
        dir_entries = {}
        for entry in scandir(starting_dir):
            if entry.name in directories:
                dir_entries[entry.name] = True
                print("%s directory found!\n" % entry.name)
        return dir_entries 


    def start_periodic_check(self, directory: str):
        """
           Occasionally check if there any new files to process.
        """
        while not(self.exit_signal):
            updated_dirs = self.check_new_files(directory)

            # Check if there are any updates.
            if updated_dirs:
                print("Updated directories %s\n" % updated_dirs.keys())

                # With new updates in hand, check if there are observers
                if self.observers:
                    # Process the new data for each updated sensor.
                    for updated_dir, sensor_updates in updated_dirs.items():
                        process_dairymgr_updates(updated_dir, sensor_updates, self)

                        self.log("Processed %s\n" % (updated_dir))
            else:
                print("No new files to process yet...\n")
                # Reset the connections until there's new data.
                self.net_ctrl.net_mgr.reset_outgoing_connections()

            # Sleep for the preset check interval
            sleep(self.periodic_check_interval)
            if self.exit_signal:
                print("Periodic check thread registered exit signal..\n")


    def check_new_files(self, starting_dir: str):
        """
           Check if there are any new files to be processed.
           :param starting_dir: The parent directory from which to start
                                the search.
        """
        updated_dirs = {}
        print("Starting new file check...\n")
        for root, dirs, files in walk(starting_dir):

            # Ignore any non-matching dirs.
            dir_name = Path(root).name
            snapshot_struct = self.proc_snapshot.snapshot_struct

            if not(dir_name in self.proc_snapshot.target_dirs):
                continue

            # Check whether any of the files have a higher mod time than latest
            for individual_file in files:
                file_path_object = Path(root + "/" + individual_file)
                file_name = file_path_object.name

                # Skip any v2 or daily rumination files for vendor three 
                if "v2" in file_name or "daily" in file_name:
                    print("Skipping v2/daily file %s\n" % file_name)
                    continue

                if 'activity' in file_name:
                    sensor_info = snapshot_struct['activity']
                elif 'hourly' in file_name:
                    sensor_info = snapshot_struct['rumination']
                else: # Directory name matches sensor name 
                    sensor_info = snapshot_struct[dir_name]


                # Get the timestamp for the latest file for the sensor.
                latest_ts = sensor_info.latest_ts

                # Check that the file creation time is greater than latest ts
                creation_time = file_path_object.stat().st_ctime
                if creation_time > latest_ts:
                    self.log("%s: creation time %s > latest time %s\n" % \
                                                    (file_name, creation_time,
                                                                     latest_ts))
                    # Get the sensor name to create the sensor update.
                    sensor_update_tuple = SensorUpdate(sensor_info.name,
                                                       individual_file,
                                                       creation_time
                                                      )
                    # Add update to the appropriate directory
                    if root in updated_dirs:
                        updated_dirs[root].append(sensor_update_tuple)
                    else:
                        updated_dirs[root] = [sensor_update_tuple] 

        # Sort the files in each updated dir by timestamps
        for directory, sensor_updates in updated_dirs.items():
            sensor_updates.sort(key=lambda update_tuple: update_tuple.timestamp)
            print("The %s directory has %s new file(s)\n" % (directory,
                                                  len(sensor_updates)))

        return updated_dirs


    def read(self,
             message: FarmBIOSMessage,
             **kwargs):
        """
           A method for reading updates requested by the peer.
           :param message: The peer message from the wire.
        """
        # Unpack the update
        update = DairyMgrSensorUpdate()
        update.ParseFromString(message.sensor.update)
        sensor_name = update.sensorName
        full_path = update.updatePath
        timestamp = update.updateTimestamp
        callback_id = message.callback.identifier
        self.log("Processing READ for Callback ID %s" % callback_id)

        # Read the updates from the file system.
        module = self.reader_map[sensor_name]
        dairymgr_proto_msgs = module.read(full_path)

        # Wrap the updates with FarmBIOSMessage descriptions
        farmbios_messages = []
        total_messages = len(dairymgr_proto_msgs)
        for index, dairymgr_msg in enumerate(dairymgr_proto_msgs):
            # Return a sensor message for any messages that are
            # supposed to trigger a callback on the compute module.
            sensor_msg = SensorRPC()
            sensor_msg.procedure.response = ResponseType.REQUESTED_DATA
            
            serialized_data = dairymgr_msg.SerializeToString()
            if callback_id != None:
                # The common case is that it is not the last message.
                if index < (total_messages - 1):
                    farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                                        metadata=sensor_msg,
                                                        data=serialized_data,
                                                        callback_id=callback_id)
                # Otherwise, it is the last message.
                # This is guaranteed to be the case because we're enumerating.
                else:
                    farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                                        metadata=sensor_msg,
                                                        data=serialized_data,
                                                        callback_id=callback_id,
                                                        is_final_response=True)
            else:
                # The common case is that it is not the last message.
                if index < (total_messages - 1):
                    farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                                        metadata=sensor_msg,
                                                        data=serialized_data)
                # Otherwise, it is the last message.
                # This is guaranteed to be the case because we're enumerating.
                else:
                    farmbios_msg = get_farmbios_message(msg_type=mod.SENSOR,
                                                        metadata=sensor_msg,
                                                        data=serialized_data,
                                                        is_final_response=True)
            farmbios_messages.append(farmbios_msg) 

        # Update the sensor timestamp assuming best effort deliver of
        # the notification to the right observers.
        sensor_tuple = self.proc_snapshot.snapshot_struct[sensor_name]
        self.proc_snapshot.update_latest_ts(sensor_tuple.name, timestamp)

        # Update the snapshot data structure for the given directory.
        self.proc_snapshot.dirty_bit = True

        # Return the list of messages and no callbacks
        return farmbios_messages, None
