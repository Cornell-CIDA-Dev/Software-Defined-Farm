from csv import DictReader 
from pathlib import Path
from typing import Any
from time import time


from sdf.dairymgr.base.spreadsheet_utils import get_value
from sdf.dairymgr.base.global_defs import (Casts, FLOOR_MSG_SIZE, CEILING_MSG_SIZE,
                                       ROW_COUNTER)
from sdf.dairymgr.proto.generated.vendorthree import rumination_eating_pb2 \
                                                    as rum_eat 
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.utils.universal_base_class import UniversalBase


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for sending rumination data.
class DailyRuminationReader(UniversalBase):

    def __init__(self):
        super().__init__()
        self.observed_activities = {} 


    def read(self, file_path: str):
        """
           Process the csv file before forwarding to server.
           :param file_path: A string.
           :return: one of the AllCowsRuminationEating protobuf objects.
        """
        filename = Path(file_path).name
        process_start_timer = time()        
        fragmented_big_file = False

        # The list of messages to be put in the queue.
        split_messages = []

        with open(file_path, newline='') as csv_fd: 
            fields = ['daily_rumination', 'daily_eating', 'daily_other',
                          'observation_time', 'local_id']

            reader = DictReader(csv_fd)
            daily_rum_msg = rum_eat.AllCowsRuminationEatingDaily()

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
                    continue

                # Otherwise add the observation to the protobuf object.
                cow_rum_msg = daily_rum_msg.allCowsRuminating.add()
                cow_rum_msg.dailyRumination = get_value(row,
                                                        'daily_rumination',
                                                        filename,
                                                        casting=Casts.FLOAT)
                cow_rum_msg.dailyEating = get_value(row, 'daily_eating',
                                                    filename,
                                                    casting=Casts.FLOAT)
                cow_rum_msg.dailyOther = get_value(row, 'daily_other',
                                                   filename,
                                                   casting=Casts.FLOAT)
                cow_rum_msg.observationTime = get_value(row,
                                                        'observation_time',
                                                        filename,
                                                        casting=Casts.STR)
                cow_rum_msg.localId = get_value(row, 'local_id',
                                                filename,
                                                casting=Casts.INT)

                # Remember the observation.
                self.observed_activities[cow_id].add(obs_time)

                # Check message size and reinitialize as needed.
                if counter == ROW_COUNTER:
                    size = daily_rum_msg.ByteSize()
                    if size >= FLOOR_MSG_SIZE and size < CEILING_MSG_SIZE:
                        # Create a new vendor three record.
                        entry = dairymgr.FarmPCMessage()
                        entry.vendorThree.filename = filename
                        entry.vendorThree.rumination.daily.CopyFrom(daily_rum_msg)
                        split_messages.append(entry)
                        daily_rum_msg = rum_eat.AllCowsRuminationEatingDaily()
                        fragmented_big_file = True
                        self.log("Last msg size %s\n" % size)

                    # Reset the counter.
                    counter == 0
                else:
                    counter += 1

            processing_time = time() - process_start_timer
            self.log("Processing %s took %s mins" % (file_path, (processing_time / 60)))

        # Check if the file has not been fragmented.
        if not(fragmented_big_file):
            entry = dairymgr.FarmPCMessage()
            entry.vendorThree.filename = filename 
            entry.vendorThree.rumination.daily.CopyFrom(daily_rum_msg)
            split_messages.append(entry)

        return split_messages 
