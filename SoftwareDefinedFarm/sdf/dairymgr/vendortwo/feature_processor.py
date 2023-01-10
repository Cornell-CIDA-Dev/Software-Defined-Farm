# System imports
from csv import DictReader
from pathlib import Path
from time import time
from typing import Any


# Local packages
from sdf.dairymgr.base.spreadsheet_utils import get_value 
from sdf.dairymgr.base.global_defs import (Casts, FLOOR_MSG_SIZE,
                                           CEILING_MSG_SIZE, ROW_COUNTER)
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.dairymgr.proto.generated.vendortwo import fresh_features_pb2 as \
                                                   freshfeat
from sdf.utils.universal_base_class import UniversalBase


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for sending fresh cow feature data.
class FeatureReader(UniversalBase):

    def __init__(self):
        super().__init__()


    def read(self, file_path: str):
        """
           Open the csv file for reading before forwarding to server.
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

        with open(file_path, newline='') as csv_fd: 
            fieldnames = ['ID', 'LACT', 'SHON', 'SHOFF', 'BOLUS', 'DIM',
                          'FDAT', 'BDAT','AGEDA','AFCDA', 'MOSFH', 'TWNS',
                          'DEADC', 'CASEX','CADOA','PL','PDIM','PFDAT',
                          'PREFR', 'PCDAT', 'PDOPN', 'DDRY', 'CINT',
                          'PDCC','BLUES', 'EASE']

            reader = DictReader(csv_fd)
            next_feat_batch = freshfeat.PerFileFreshFeatureData()

	    # Determines the appropriate number of rows before checking size.
            counter = 0

            for row in reader:

                # Check if we have reached the end of data.
                if row['ID'] == "Total:":

                    # Check if the file has been fragmented.
                    if not(fragmented_big_file):
                        entry = dairymgr.FarmPCMessage()
                        entry.vendorTwo.filename = filename
                        entry.vendorTwo.fresh_features.CopyFrom(next_feat_batch)
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
                    self.log("%s split into %d chunks\n" % (file_path, message_chunk_counter))

                    return split_messages

                cow_feat_msg = next_feat_batch.allFreshEntries.add()
                cow_feat_msg.key.id = get_value(row, 'ID', file_path,
                                                     casting=Casts.INT) 
                cow_feat_msg.key.lact = get_value(row, 'LACT',
                                                   file_path, casting=Casts.INT)
                cow_feat_msg.shon = get_value(row, 'SHON', file_path,
                                                   casting=Casts.STR)
                cow_feat_msg.shoff = get_value(row, 'SHOFF', file_path,
                                                   casting=Casts.STR)
                temp_bolus  = get_value(row, 'BOLUS', file_path,
                                             casting=Casts.STR)
                if temp_bolus != "-":
                    cow_feat_msg.bolus = temp_bolus
                cow_feat_msg.dim = get_value(row, 'DIM', file_path,
                                                   casting=Casts.INT)
                cow_feat_msg.fdat = get_value(row, 'FDAT',
                                                   file_path, casting=Casts.STR) 
                cow_feat_msg.bdat = get_value(row, 'BDAT', file_path,
                                                casting=Casts.STR)
                cow_feat_msg.ageda = get_value(row, 'AGEDA', file_path,
                                                casting=Casts.INT)
                cow_feat_msg.afcda = get_value(row, 'AFCDA',
                                                           file_path,
                                                        casting=Casts.INT)
                cow_feat_msg.mosfh = get_value(row, 'MOSFH',
                                                                file_path,
                                                         casting=Casts.STR)
                cow_feat_msg.calving.twns = get_value(row,'TWNS', file_path,
                                                         casting=Casts.INT)
                cow_feat_msg.calving.deadc = get_value(row,
                                                                 'DEADC',
                                                                 file_path,
                                                          casting=Casts.INT) 
                cow_feat_msg.calving.casex = get_value(row,
                                                                 'CASEX',
                                                                 file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.calving.cadoa = get_value(row,
                                                                 'CADOA',
                                                                 file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.lactData.pl = get_value(row, 'PL', file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.lactData.pdmi = get_value(row, 'PDIM', file_path,
                                                   casting=Casts.INT)
                cow_feat_msg.gestation.prefr = get_value(row, 'PREFR',
                                                                  file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.gestation.ddry = get_value(row, 'DDRY',
                                                             file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.gestation.cint = get_value(row, 'CINT',
                                                             file_path,
                                                          casting=Casts.INT)
                cow_feat_msg.gestation.pdcc = get_value(row, 'PDCC',
                                                             file_path,
                                                          casting=Casts.INT)

                # Any value not 0/1 should be 0, where 0 == False and 1 == True
                blues_value = get_value(row, 'BLUES', file_path,
                                                          casting=Casts.INT)
                if blues_value == 1:
                    cow_feat_msg.gestation.blues = True
                else:
                    cow_feat_msg.gestation.blues = False

                cow_feat_msg.gestation.ease = get_value(row, 'EASE',
                                                             file_path,
                                                          casting=Casts.INT)
                # Check message size and reinitialize as needed.
                if counter == ROW_COUNTER:
                    size = next_feat_batch.ByteSize()
                    if size < FLOOR_MSG_SIZE or size >= CEILING_MSG_SIZE:
                        print('%s: MSG size outside of window: %d' % (self.__class__.__name__, size) )
                    # Create a new vendor two record regardless of window size.
                    # This is based on evidence from preliminary data pushes
                    # which shows that most messages are less than 8KB
 
                    entry = dairymgr.FarmPCMessage() 
                    entry.vendorTwo.filename = filename
                    entry.vendorTwo.fresh_features.CopyFrom(next_feat_batch)
                    split_messages.append(entry)

                    # Prep next batch
                    next_feat_batch = freshfeat.PerFileFreshFeatureData()
                    fragmented_big_file = True
                    message_chunk_counter += 1

                    # Reset the counter
                    counter = 0
                else:
                    counter += 1
