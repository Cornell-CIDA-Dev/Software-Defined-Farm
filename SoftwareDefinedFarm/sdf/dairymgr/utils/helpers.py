# System imports
from argparse import ArgumentParser
from pathlib import Path
from pickle import load
from socket import socket
from time import sleep 
from typing import List, Any, Optional, Dict


# Local packages
from sdf.dairymgr.base.global_defs import (SensorUpdate, THROTTLE_INTERVAL,
                                           MAX_QUEUE_SIZE, SNAPSHOT_INTERVAL)
from sdf.dairymgr.proto.dairymgr_pb2 import FarmPCMessage
from sdf.dairymgr.proto.generated.update_pb2 import DairyMgrSensorUpdate
from sdf.dairymgr.snapshot import Snapshot
from sdf.helper_typedefs import Modules as mod
from sdf.farmbios.helpers import get_farmbios_message
from sdf.farmbios.proto.compute_pb2 import ComputeRPC
from sdf.farmbios.proto.farmbios_pb2 import FarmBIOSMessage
from sdf.farmbios.proto.sensor_pb2 import SensorRPC
from sdf.farmbios.proto.shared_pb2 import CallType, ResponseType
from sdf.network.status import CommunicationStatus as comstatus
from sdf.network.network_controller import NetworkController 
from sdf.sensors.base_sensor import SensorModule

# Third party packages
from google.protobuf.internal.encoder import _VarintBytes


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


def process_dairymgr_updates(homedir: str,
                             sensor_updates : List[SensorUpdate],
                             sensor_module: Any):
    """
       Process new files in an updated sensor directory.
       :param homedir: The full qualified path to the directory.
       :param sensor_updates: The individual updated files.
       :param sensor_module: The sensor module in charge of notifications.
       :rtype: A list of FarmBIOSMessage objects.
    """
    target_dir = homedir + "/"
    for update_tuple in sensor_updates:
        sensor_name = update_tuple.sensor_name

        # Unpack the full path and timestamp of the updated file.
        full_path = target_dir + update_tuple.file_name
        update_timestamp = update_tuple.timestamp

        # Build the full path to the update file
        full_path = target_dir + update_tuple.file_name

        # Create the update notification to be sent to observers
        update = DairyMgrSensorUpdate(sensorName=sensor_name,
                                      updatePath=full_path,
                                      updateTimestamp=update_timestamp)
        compute_msg = ComputeRPC()
        compute_msg.procedure.call = CallType.RCV_SENSOR_NOTIFICATION
        compute_msg.update = update.SerializeToString() 
                                           
        # Serialize message and notify observers of the new update. 
        farmbios_msg = get_farmbios_message(mod.COMPUTE, compute_msg)
        sensor_module.set_changed()
        sensor_module.notify(farmbios_msg)


def deliver(message: FarmPCMessage,
            config: Any
           ):
    """
       Forward the processed file's data to the cloud aggregator.
       :param message: A pointer to the underlying network service.
       :param config: The config which has access to the underlying
                      network and a tuple of the cloud aggregator IP address. 
    """
    # Get the connection to the storage aggregator
    status, connection = config.get_or_set_peer_conn(mod.STORAGE,
                                                     config.storage_address
                                                     ) 

    if status == comstatus.SUCCESS:
        # Serialize message
        size = message.ByteSize()
        print("The message size is %s\n" % size)
        serialized_entry = _VarintBytes(size)
        serialized_entry += message.SerializeToString()

        # Put it in outgoing queues
        msg_queue = config.net_ctrl.net_mgr.message_queues[connection]
        msg_queue.put(serialized_entry)
        if msg_queue.qsize() >= MAX_QUEUE_SIZE:
            print("Message queue size %d\n" % msg_queue.qsize())

            print("Throttling Sleep: %s secs\n" % THROTTLE_INTERVAL)
            sleep(THROTTLE_INTERVAL)

        # Check if connection is being watched as writable.
        if connection not in config.net_ctrl.net_mgr.outputs:
            config.net_ctrl.net_mgr.outputs.append(connection)

        return comstatus.SUCCESS
    else:
        print("No connection to cloud aggregator: (%s:%s)\n" % \
                                                   (config.storage_address[0],
                                                    config.storage_address[1]))
        print("Reconnect attempt returned %s\n" % status.name)
        print("Skipping send for current message\n")
        return None


def load_snapshot(default_snapshot_path: str,
                  target_dirs: List,
                  user_snapshot_path: Optional[str] = None
                 ):
    """
       Load a previous snapshot from memory or create a new one.
       :param default_snapshot_path: The default full path.
       :param target_dirs: Directories containing sensor reports.
       :param user_snapshot_path: The user specified full path.
       :rtype: A Snapshot object either loaded from file or newly created.
    """
    proc_snapshot = None

    # Get a path object to the default snapshot filename
    local_snapshot = Path(default_snapshot_path)

    # Take user snapshot path first.
    if user_snapshot_path: 
        user_snapshot = Path(user_snapshot_path)
        if user_snapshot.exists() and user_snapshot.is_file():
            print("Loading user snapshot at %s\n" % user_snapshot_path)
            with open(user_snapshot_path, 'rb') as fd:
                proc_snapshot = load(fd)
        else: # Take how the user wants to name their snapshot
            proc_snapshot = Snapshot(SNAPSHOT_INTERVAL, user_snapshot_path, 
                                     target_dirs)
         

    # Take a local existing snapshot second.
    elif local_snapshot.exists() and local_snapshot.is_file(): 
        print("Loading default snapshot at %s\n" % default_snapshot_path)
        with open(default_snapshot_path, 'rb') as fd:
            proc_snapshot = load(fd)

    # Simply create a new one to load from later.
    else: 
        proc_snapshot = Snapshot(SNAPSHOT_INTERVAL, default_snapshot_path,
                                 target_dirs)

    return proc_snapshot


def check_on_threads(future):
    """
       :param future: The future object associated with a function call.
    """
    ft_exception = future.exception()
    if ft_exception != None: # Future failed somehow
       print("A future somewhere raised a < %s > exception\n" %  \
             ft_exception.__str__())
