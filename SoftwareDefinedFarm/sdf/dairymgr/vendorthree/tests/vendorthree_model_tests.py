import unittest
import inspect
from pathlib import Path
from os import walk


from sdf.dairymgr.vendorthree.tests import processor_factories as p_factories


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

# Define Globals
HIGHEST_COW_ID = 13000
HIGHEST_HOURLY_EATING = 200 
HIGHEST_DAILY_RUMINATION = 1700
HIGHEST_DAILY_ACTIVITY = 1350 

# @brief: A class for testing the hourly rumination data processor.
class TestHourlyRuminationProcessorClass(unittest.TestCase):


    def test_read(self):
        """ Test the read method using a rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        rumination_processor = p_factories.HourlyRuminationFactory()
        file_path = 'vendorthree_test_data/rumination_eating_hourly_03202020_1223.csv' 
        entries = rumination_processor.read(file_path)
        for entry in entries:
            for record in entry.vendorThree.rumination.hourly.allCowsRuminating:
                self.assertLess(record.hourlyEating, HIGHEST_HOURLY_EATING)
                self.assertLessEqual(record.localId, HIGHEST_COW_ID)
                self.assertIn("2020", record.observationTime)

            # Check that the filename is initialized properly.
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorThree.filename)


# @brief: A class for testing the daily rumination data processor.
class TestDailyRuminationProcessorClass(unittest.TestCase):


    def test_read(self):
        """ Test the read method using a daily rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        rumination_processor = p_factories.DailyRuminationFactory()
        file_path = "vendorthree_test_data/rumination_eating_daily_03202020_1223.csv"
        entries = rumination_processor.read(file_path)
        for entry in entries:
            for record in entry.vendorThree.rumination.daily.allCowsRuminating:
                self.assertLessEqual(record.dailyEating, HIGHEST_DAILY_RUMINATION)
                self.assertLessEqual(record.localId, HIGHEST_COW_ID)
                self.assertIn("2020", record.observationTime)

            # Check that the filename is initialized properly.
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorThree.filename)


# @brief: A class for testing the activity data processor.
class TestActivityProcessorClass(unittest.TestCase):


    def test_read(self):
        """ Test the read method using a rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        activity_processor = p_factories.ActivityFactory()
        file_path = "vendorthree_test_data/activity_03202020_1224.csv"
        entries = activity_processor.read(file_path)
        for entry in entries:
            for act_record in entry.vendorThree.activity.activityEntries:
                self.assertLessEqual(act_record.activity, HIGHEST_DAILY_ACTIVITY)
                self.assertLessEqual(act_record.localId, HIGHEST_COW_ID)
                self.assertIn("2020", act_record.observationTime)

            # Check that the filename is initialized properly.
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorThree.filename)


