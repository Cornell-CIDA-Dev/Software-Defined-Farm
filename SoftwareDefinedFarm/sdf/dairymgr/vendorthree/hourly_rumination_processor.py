#System packages
from csv import DictReader 
from time import time
from typing import Any
from pathlib import Path


# Local packages
from sdf.dairymgr.base.spreadsheet_utils import get_value
from sdf.dairymgr.base.global_defs import (Casts, FLOOR_MSG_SIZE,
                                           CEILING_MSG_SIZE, ROW_COUNTER)
from sdf.dairymgr.proto.generated.vendorthree import rumination_eating_pb2 \
                                                        as rum_eat 
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.utils.universal_base_class import UniversalBase


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for sending rumination data.
class HourlyRuminationReader(UniversalBase):

    def __init__(self):
        super().__init__()
        self.observed_activities = {} 


    def read(self, file_path: str):
        """
           Process the csv file before forwarding to server.
           :param file_path: A string.
           :return: A list of VendorThreeEntry protobuf objects.
        """
        filename = Path(file_path).name
        process_start_timer = time()        
        fragmented_big_file = False

        # The list of and counter of messages to be put in the queue.
        split_messages = []
        message_chunk_counter = 0

        with open(file_path, newline='') as csv_fd: 

            reader = DictReader(csv_fd)
            hourly_rum_msg = rum_eat.AllCowsRuminationEatingHourly()

            # Determines the appropriate number of rows before checking size.
            counter = 0

            for row in reader:

                # Check if we have observed any data for the cow.
                cow_id = row['local_id']
                if not(cow_id in self.observed_activities):
                    self.observed_activities[cow_id] = set()

                # Check if we have observed the activity for this cow.
                obs_time = row['observation_time']
                if obs_time in self.observed_activities[cow_id]:
                    #print("Already observed %s for %s\n" % (obs_time, cow_id))
                    continue

                # Otherwise add the observation to the protobuf object.
                cow_rum_msg = hourly_rum_msg.allCowsRuminating.add()
                cow_rum_msg.hourlyRumination = get_value(row,
                                                           'hourly_rumination',
                                                              file_path,
                                                         casting=Casts.FLOAT)
                cow_rum_msg.hourlyEating = get_value(row, 'hourly_eating',
                                                     file_path,
                                                     casting=Casts.FLOAT)
                cow_rum_msg.hourlyOther = get_value(row, 'hourly_other',
                                                    file_path,
                                                    casting=Casts.FLOAT)
                cow_rum_msg.observationTime = get_value(row,
                                                        'observation_time',
                                                        file_path,
                                                        casting=Casts.STR)
                cow_rum_msg.localId = get_value(row, 'local_id',
                                                file_path,
                                                casting=Casts.INT)

                # Remember the observation.
                self.observed_activities[cow_id].add(obs_time)

                # Check message size and reinitialize as needed.
                if counter == ROW_COUNTER:
                    size = hourly_rum_msg.ByteSize()
                    if size < FLOOR_MSG_SIZE or size >= CEILING_MSG_SIZE:
                        print('%s: MSG size outside of window: %d' % (self.__class__.__name__, size) )
                    # Create a new vendor three record regardless of window size.
                    # This is based on evidence from preliminary data pushes
                    # which shows that most messages are less than 8KB
                    entry = dairymgr.FarmPCMessage()
                    entry.vendorThree.filename = filename
                    entry.vendorThree.rumination.hourly.CopyFrom(hourly_rum_msg)
                    split_messages.append(entry)
                    hourly_rum_msg = rum_eat.AllCowsRuminationEatingHourly()
                    fragmented_big_file = True
                    message_chunk_counter += 1

                    self.log("Last msg size %s\n" % size)

                    # Reset the counter
                    counter = 0
                else:
                    counter += 1

            processing_time = time() - process_start_timer
            proc_time_mins = int(processing_time/60)
            if proc_time_mins >= 1:
                processing_time = proc_time_mins
                unit = "minutes"
            else:
                unit = "seconds"
            self.log("Processing %s took %s %s\n" % (file_path,
                                                  processing_time,
                                                  unit))
         
        # Check if the file has not been fragmented.
        if not(fragmented_big_file) or counter != ROW_COUNTER:
            entry = dairymgr.FarmPCMessage()
            entry.vendorThree.filename = filename 
            entry.vendorThree.rumination.hourly.CopyFrom(hourly_rum_msg)
            split_messages.append(entry)
            message_chunk_counter += 1

        # Log the number of chunks for system debugging.
        self.log("%s file into %d chunks\n" % (file_path, message_chunk_counter))

        return split_messages 
