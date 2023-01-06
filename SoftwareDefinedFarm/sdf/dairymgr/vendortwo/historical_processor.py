# System packages
from time import time
from typing import Any
from pathlib import Path


# Local packages
from sdf.dairymgr.base.spreadsheet_utils import (get_value, ExcelReader)
from sdf.dairymgr.base.global_defs import (FLOOR_MSG_SIZE, CEILING_MSG_SIZE,
                                           ROW_COUNTER, Casts) 
from sdf.network.status import CommunicationStatus as comstatus
from sdf.dairymgr.proto.generated.vendortwo import historical_pb2 as historical 
from sdf.dairymgr.proto import dairymgr_pb2 as dairymgr 
from sdf.utils.universal_base_class import UniversalBase


# Third party packages

__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for processing historical data.
class HistoricalReader(UniversalBase):

    def __init__(self):
        super().__init__()


    def read(self, file_path: str):
        """
           Proess the excel file before forwarding to server.
           :param file_path: A string.
           :rtype: A list of FarmPCMessage objects.
        """
        filename = Path(file_path).name
        process_start_timer = time()        

        # Flag to keep track of whether file is split into different messages.
        fragmented_big_file = False

        # The list and counter of messages to be put in the queue.
        split_messages = []
        message_chunk_counter = 0

        # The interface to an excel reader for the file.
        reader = ExcelReader(file_path, data_only=True)

        next_hist_batch = historical.PerFileHistoricalData()

	# Determines the appropriate number of rows before checking size.
        counter = 0

        for row in range(2, reader.active_sheet.max_row+1):
            chst_msg = next_hist_batch.allHistEntries.add()
            chst_msg.key.id = self.get_value(reader, row, 1, Casts.INT)
            chst_msg.key.lact = self.get_value(reader, row, 2, Casts.INT)
            chst_msg.key.pen = self.get_value(reader, row, 3, Casts.INT)
            value = self.get_value(reader, row, 4, Casts.STR)
            if value != None:
                chst_msg.mosfh = value.strip()
            chst_msg.calving.deadc = self.get_value(reader, row, 6, Casts.INT)
            chst_msg.calving.casex = self.get_value(reader, row, 7, Casts.INT)
            chst_msg.calving.cadoa = self.get_value(reader, row, 8, Casts.INT)
            chst_msg.calving.ddat = self.get_value(reader, row, 9, Casts.STR)
            chst_msg.gestation.cu = self.get_value(reader, row, 10, Casts.STR)
            chst_msg.gestation.due = self.get_value(reader, row, 11, Casts.STR)
            chst_msg.fatMilkProtein.totm = self.get_value(reader, row, 12,
                                                          Casts.INT)
            chst_msg.fatMilkProtein.totf = self.get_value(reader, row, 13,
                                                          Casts.INT)
            chst_msg.fatMilkProtein.totp = self.get_value(reader, row, 14,
                                                          Casts.INT)
            chst_msg.tbrd = self.get_value(reader, row, 15, Casts.INT)
            chst_msg.specificHealthEvents.tmet = self.get_value(reader, row,
                                                                16, Casts.INT)
            chst_msg.specificHealthEvents.trp = self.get_value(reader, row,
                                                               17, Casts.INT)
            chst_msg.mastitisEvents.nmast = self.get_value(reader, row, 18,
                                                           Casts.INT)
            chst_msg.mastitisEvents.mt030 = self.get_value(reader, row, 19,
                                                           Casts.INT)
            chst_msg.mastitisEvents.mtt30 = self.get_value(reader, row, 20,
                                                           Casts.INT)
            chst_msg.lameEvents.nlame = self.get_value(reader, row, 21,
                                                       Casts.INT)
            chst_msg.lameEvents.lm030 = self.get_value(reader, row, 22,
                                                       Casts.INT)
            chst_msg.lameEvents.lmn30 = self.get_value(reader, row, 23,
                                                       Casts.INT)
            chst_msg.specificHealthEvents.nket = self.get_value(reader, row,
                                                                24, Casts.INT)
            chst_msg.specificHealthEvents.kt030 = self.get_value(reader, row,
                                                                 25, Casts.INT)
            chst_msg.specificHealthEvents.ket30 = self.get_value(reader, row,
                                                                 26, Casts.INT)
            chst_msg.specificHealthEvents.nindig = self.get_value(reader, row,
                                                                  27, Casts.INT)
            chst_msg.specificHealthEvents.id030 = self.get_value(reader, row,
                                                                 28, Casts.INT)
            chst_msg.specificHealthEvents.idg30 = self.get_value(reader, row,
                                                                 29, Casts.INT)
            chst_msg.specificHealthEvents.nda = self.get_value(reader, row, 30,
                                                               Casts.INT)
            chst_msg.specificHealthEvents.da030 = self.get_value(reader, row,
                                                                 31, Casts.INT)
            chst_msg.specificHealthEvents.da30 = self.get_value(reader, row,
                                                                32, Casts.INT)
            chst_msg.generalHealthEvents.pldz_all = self.get_value(reader, row,
                                                                   33,
                                                                   Casts.INT)
            chst_msg.generalHealthEvents.pl_dz_n = self.get_value(reader, row,
                                                                  34, Casts.INT)
            chst_msg.generalHealthEvents.pldz_30 = self.get_value(reader, row,
                                                                  35, Casts.INT)
            chst_msg.generalHealthEvents.pl_dz30_n = self.get_value(reader, row,
                                                                    36,
                                                                    Casts.INT)
            chst_msg.generalHealthEvents.pldz_31_dry = self.get_value(reader,
                                                                      row,
                                                                      37,
                                                                      Casts.INT)
            chst_msg.generalHealthEvents.pl_dz31_dry_n = self.get_value(reader,
                                                                        row,
                                                                        38,
                                                                      Casts.INT)

            # Check message size and reinitialize as needed.
            if counter == ROW_COUNTER:
                size = next_hist_batch.ByteSize()
                if size < FLOOR_MSG_SIZE or size >= CEILING_MSG_SIZE:
                    print('%s: MSG size outside of window: %d' % (self.__class__.__name__, size) )

                # Create a new dairycomp record regardless of window size.
                # This is based on evidence from preliminary data pushes
                # which shows that most messages are less than 8KB
                entry = dairymgr.FarmPCMessage()
                entry.filename = filename
                entry.vendorTwo.historical.CopyFrom(next_hist_batch)
                split_messages.append(entry)

                # Prep next batch
                next_hist_batch = historical.PerFilePredictionData()
                fragmented_big_file = True
                message_chunk_counter += 1

                # Reset the counter
                counter = 0
            else:
                counter += 1

        # Check if the file has been fragmented.
        if not(fragmented_big_file) or counter != ROW_COUNTER:
            entry = dairymgr.FarmPCMessage()
            entry.vendorTwo.filename = filename
            entry.vendorTwo.historical.CopyFrom(next_hist_batch)
            split_messages.append(entry)
            message_chunk_counter += 1

        processing_time = time() - process_start_timer
        self.log("Processing %s took %s mins" % (file_path,
                                           (processing_time / 60)))

        # Log the number of chunks for system debugging.
        self.log("%s split into %d chunks\n" % (file_path, message_chunk_counter))

        return split_messages 


    def get_value(self, reader, row_num, column, exp_type):
        """
           Get the value in a given row and column in excel sheet if it exists.
           :param reader: an ExcelReader object .
           :param row_num: An int.
           :param column: An int.
           :param exp_type: A Casts enum.
        """
        cell = reader.get_cell(row_num, column)
        value = None

        # Checking for TYPE_NULL is hard because it's the same as
        # the character for numeric types in openpyxl ('n')
        # Therefore we just check what null values may look like.
        null_vals = ["--", "", None]

        if cell.value in null_vals:
            if exp_type == Casts.INT or exp_type == Casts.SINT:
                value = 0
            elif exp_type == Casts.FLOAT:
                value = 0.0
            elif exp_type == Casts.STR:
                value = ""
            elif exp_type == Casts.BOOL:
                value = None
            else:
                raise ValueError("Unknown type (%s) at row: %d, col: %d!\n" \
                                  % (cell.data_type, row_num, column))
        else:
            if exp_type == Casts.INT or exp_type == Casts.SINT:
                value = int(cell.value)
            elif exp_type == Casts.STR:
                value = str(cell.value)
            elif exp_type == Casts.FLOAT:
                value = float(cell.value)
            else: # Bool
                if cell.value == "No":
                    value = False
                else:
                    value = True
        return value
