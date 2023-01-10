import unittest
import inspect
from pathlib import Path


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
        file_path = "vendorone_test_data/milk_yield_07282020_1500.xlsx"

        entries = milk_yield_processor.read(file_path)
        # Each entry can be one of multiple PC messages if the size is too big.
        cow_ids = [1, 5099, 12803]
        for entry in entries:
            # Pick 10 random cells and check values/types
            for record in entry.vendorOne.milk.entries:
                if record.key.id in cow_ids:
                    self.assertNotEqual(record.m_yield.yield_1, '--') 
                    self.assertEqual(type(record.key.id), int)
                    self.assertEqual(type(record.key.group_today), int)
                    self.assertEqual(type(record.key.group_yesterday), int)
                    self.assertEqual(type(record.status.lactation), int)
                    self.assertEqual(type(record.status.dim), int)
                    self.assertEqual(type(record.status.status), str)
                    self.assertEqual(type(record.m_yield.daily_yield), float)
                    self.assertEqual(type(record.m_yield.yield_1), float)
                    self.assertEqual(type(
                                    record.protein.daily_protein_dev_perc),
                                            int)
                    self.assertTrue(record.m_yield.daily_avg_yield <= 140.0)
                    self.assertNotEqual(record.scc.daily_scc, "800+")
                self.assertIn(record.key.wrong_group, [True, False])

            # Check that the filename is initialized properly.
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorOne.filename)
