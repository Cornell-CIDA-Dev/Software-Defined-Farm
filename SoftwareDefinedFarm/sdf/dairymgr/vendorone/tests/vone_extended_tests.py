import unittest
import inspect
from pathlib import Path
from os import walk


from sdf.dairymgr.vendorone.tests import vone_processor_factory as vone_factory


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for testing the hourly rumination data processor.
class TestMilkYieldProcessorClass(unittest.TestCase):


    def test_process_file(self):
        """ Test the read method using a rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        milk_yield_processor = vone_factory.MilkYieldFactory()
        dir_prefix = 'vendorone_test_data/extended_data/'
        for _, _, files in walk(dir_prefix):
            for file_path in files:
                full_path = dir_prefix + file_path
                print("Processing %s\n" % full_path)
                entries = milk_yield_processor.read(full_path)

                # Each entry can be one of multiple PC messages if the size is too big.
                cow_ids = [1, 5099, 12803]
                for entry in entries:
                    # Pick 10 random cells and check values/types
                    for record in entry.vendorOne.milk.entries:
                        if record.key.id in cow_ids:
                            self.assertNotEqual(record.m_yield.yield_1, '--') 
                            self.assertIsInstance(record.key.id, int)
                            self.assertIsInstance(record.key.group_today, int)
                            self.assertIsInstance(record.key.group_yesterday, int)
                            self.assertIsInstance(record.status.lactation, int)
                            self.assertIsInstance(record.status.dim, int)
                            self.assertIsInstance(record.status.status, str)
                            self.assertIsInstance(record.m_yield.daily_yield, float)
                            self.assertIsInstance(record.m_yield.yield_1, float)
                            self.assertIsInstance(
                                          record.protein.daily_protein_dev_perc,
                                                  int)
                            self.assertTrue(record.m_yield.daily_avg_yield <= 140.0)
                            self.assertNotEqual(record.scc.daily_scc, "800+")
                        self.assertIn(record.key.wrong_group, [True, False])

                    # Check that the filename is initialized properly.
                    filename = Path(file_path).name
                    self.assertEqual(filename, entry.vendorOne.filename)
