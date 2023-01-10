# System packages
from csv import DictReader
from pathlib import Path
from time import time
from typing import Any


# Local packages
from sdf.dairymgr.base.spreadsheet_utils import get_value 
from sdf.dairymgr.base.global_defs import (Casts, FLOOR_MSG_SIZE,
                                           CEILING_MSG_SIZE, ROW_COUNTER)
from sdf.dairymgr.proto.generated.vendortwo import pencap_pb2 as pc
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.utils.universal_base_class import UniversalBase


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for sending pen capacity data.
class PenCapReader(UniversalBase):

    def __init__(self):
        super().__init__()


    def read(self, file_path: str):
        """
           Open the excel file for reading before forwarding to server.
           :param file_path: A string.
           :return: A list of FarmPCMessage protobuf objects.
        """
        filename = Path(file_path).name
        process_start_timer = time()        

        # Flag to keep track of whether file is split into different messages.
        fragmented_big_file = False

        # The list and counter of messages to be put in the queue.
        split_messages = []
        message_chunk_counter = 0

        with open(file_path, newline='') as csvfile:
            fieldnames = ['By PEN', 'Pct', 'Count', 'AvSTLCT', 'AvPENCP']
            reader = DictReader(csvfile)
            next_pencap_batch = pc.PerFilePenCapacityData()

	    # Determines the appropriate number of rows before checking size.
            counter = 0

            for row in reader:

                # Check if we have reached the end of data.
                if ('=' in row['By PEN']):

                    # Check if the file has been fragmented.
                    if not(fragmented_big_file):
                        entry = dairymgr.FarmPCMessage() 
                        entry.vendorTwo.filename = filename
                        entry.vendorTwo.pen_cap.CopyFrom(next_pencap_batch)
                        split_messages.append(entry)

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

                    # Log the number of chunks for system debugging.
                    self.log("%s split into %d chunks\n" % (file_path,
                                                     message_chunk_counter))

                    return split_messages

                else:
                    data = next_pencap_batch.all_pens.add()
                    data.byPen = get_value(row, 'By PEN', file_path,
                                                 Casts.INT) 
                    data.pct = get_value(row, 'Pct', file_path,
                                                 Casts.INT) 
                    data.count = get_value(row, 'Count', file_path,
                                                 Casts.INT) 
                    data.avgstlct = get_value(row, 'AvSTLCT', file_path,
                                                 Casts.INT) 
                    data.avPencp = get_value(row, 'AvPENCP',
                                                        file_path, Casts.INT)
                    # Check message size and reinitialize as needed.
                    if counter == ROW_COUNTER:
                        size = next_pencap_batch.ByteSize()
                        if size < FLOOR_MSG_SIZE or size >= CEILING_MSG_SIZE:
                            print('%s: MSG size outside of window: %d' %
                                        (self.__class__.__name__, size) )
                        # Create a new vendor two record regardless of window size.
                        # This is based on evidence from preliminary data pushes
                        # which shows that most messages are less than 8KB
                        entry = dairymgr.FarmPCMessage() 
                        entry.vendorTwo.filename = filename
                        entry.vendorTwo.pen_cap.CopyFrom(next_pencap_batch)
                        split_messages.append(entry)

                        # Prep next batch
                        next_pencap_batch = pc.PerFilePenCapacityData()
                        fragmented_big_file = True
                        message_chunk_counter += 1

                        # Reset the counter
                        counter = 0
                    else:
                        counter += 1
            return split_messages
