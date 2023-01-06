# System imports
from csv import DictReader
from pathlib import Path
from time import time
from typing import Any


# Local packages
from sdf.dairymgr.base.spreadsheet_utils import get_value 
from sdf.dairymgr.base.global_defs import (Casts, FLOOR_MSG_SIZE, CEILING_MSG_SIZE,
                                        ROW_COUNTER) 
from sdf.dairymgr.proto.generated.vendortwo import prediction_pb2 as prediction 
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.utils.universal_base_class import UniversalBase


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for processing prediction data.
class PredictionReader(UniversalBase):

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

        with open(file_path, newline='') as csv_fd:
            col_names = ['ID', 'LACT', 'SHON', 'SHOFF', 'DIM', 'FDAT',
                         'BDAT','AGEDA','BLUES', 'EASE','NMAST', 'NLAME',
                         'TRP', 'TMET', 'NKET','NINDG','NDA', 'PEN']
            reader = DictReader(csv_fd)
            next_pred_batch = prediction.PerFilePredictionData()

	    # Determines the appropriate number of rows before checking size.
            counter = 0

            for row in reader:

                # Check if we have reached the end of data.
                if row['ID'] == "Total:":

                    # Check if the file has been fragmented.
                    if not(fragmented_big_file):
                        entry = dairymgr.FarmPCMessage()
                        entry.vendorTwo.filename = filename
                        entry.vendorTwo.prediction.CopyFrom(next_pred_batch)
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

                pred_msg = next_pred_batch.allPredEntries.add()
                pred_msg.key.id = get_value(row, 'ID',
                                             file_path, casting=Casts.INT)
                pred_msg.key.lact = get_value(row, 'LACT', file_path,
                                               casting=Casts.INT)
                pred_msg.key.pen = get_value(row, 'PEN',
                                              file_path, casting=Casts.INT)
                pred_msg.shon = get_value(row, 'SHON',
                                              file_path, casting=Casts.STR)
                pred_msg.shoff = get_value(row, 'SHOFF',
                                              file_path, casting=Casts.STR)
                pred_msg.dim = get_value(row, 'DIM', file_path,
                                              casting=Casts.INT)
                pred_msg.fdat = get_value(row, 'FDAT',
                                               file_path, casting=Casts.STR)
                pred_msg.bdat = get_value(row, 'BDAT',
                                               file_path, casting=Casts.STR)
                pred_msg.ageda = get_value(row, 'AGEDA',
                                              file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.nmast = get_value(row,
                                     'NMAST', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.nlame = get_value(row,
                                     'NLAME', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.trp = get_value(row,
                                     'TRP', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.tmet = get_value(row,
                                     'TMET', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.nket = get_value(row,
                                     'NKET', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.nindig = get_value(row,
                                     'NINDG', file_path, casting=Casts.INT)
                pred_msg.observedHealthEvents.nda = get_value(row,
                                     'NDA', file_path, casting=Casts.INT)
                
                # Check message size and reinitialize as needed.
                if counter == ROW_COUNTER:
                    size = next_pred_batch.ByteSize()
                    if size < FLOOR_MSG_SIZE or size >= CEILING_MSG_SIZE:
                        print('%s: MSG size outside of window: %d' % (self.__class__.__name__, size) )
                    # Create a new dairycomp record regardless of window size.
                    # This is based on evidence from preliminary data pushes
                    # which shows that most messages are less than 8KB
                    entry = dairymgr.FarmPCMessage()
                    entry.vendorTwo.filename = filename
                    entry.vendorTwo.prediction.CopyFrom(next_pred_batch)
                    split_messages.append(entry)

                    # Prep next batch
                    next_pred_batch = prediction.PerFilePredictionData()
                    fragmented_big_file = True
                    message_chunk_counter += 1

                    # Reset the counter
                    counter = 0
                else:
                    counter += 1
