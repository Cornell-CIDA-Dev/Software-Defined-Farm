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
        dir_prefix = 'vendorthree_test_data/hourlydata/'
        for _, _, files in walk(dir_prefix):
            for file_path in files:
                full_path = dir_prefix + file_path 
                entries = rumination_processor.read(full_path)
                for entry in entries:
                    for record in entry.vendorThree.rumination.hourly.allCowsRuminating:
                        self.assertLess(record.hourlyEating, HIGHEST_HOURLY_EATING)
                        self.assertLessEqual(record.localId, HIGHEST_COW_ID)
                        years = ["2019", "2020"]
                        observation_year = record.observationTime.split('-')[0]
                        self.assertIn(observation_year, years)

                    # Check that the filename is initialized properly.
                    filename = Path(full_path).name
                    self.assertEqual(filename, entry.vendorThree.filename)


# @brief: A class for testing the daily rumination data processor.
class TestDailyRuminationProcessorClass(unittest.TestCase):


    def test_read(self):
        """ Test the read method using a daily rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        rumination_processor = p_factories.DailyRuminationFactory()
        dir_prefix = 'vendorthree_test_data/dailydata/'
        for _, _, files in walk(dir_prefix):
            for file_path in files:
                full_path = dir_prefix + file_path 
                entries = rumination_processor.read(full_path)
                for entry in entries:
                    for record in entry.vendorThree.rumination.daily.allCowsRuminating:
                        self.assertLessEqual(record.dailyEating, HIGHEST_DAILY_RUMINATION)
                        self.assertLessEqual(record.localId, HIGHEST_COW_ID)
                        years = ["2019", "2020"]
                        observation_year = record.observationTime.split('-')[0]
                        self.assertIn(observation_year, years)

                    # Check that the filename is initialized properly.
                    filename = Path(full_path).name
                    self.assertEqual(filename, entry.vendorThree.filename)


# @brief: A class for testing the activity rumination data processor.
class TestActivityProcessorClass(unittest.TestCase):


    def test_read(self):
        """ Test the read method using a rumination data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        activity_processor = p_factories.ActivityFactory()
        dir_prefix = 'vendorthree_test_data/activitydata/'
        for _, _, files in walk(dir_prefix):
            for file_path in files:
                full_path = dir_prefix + file_path 
                entries = activity_processor.read(full_path)
                for entry in entries:
                    for act_record in entry.vendorThree.activity.activityEntries:
                        self.assertLessEqual(act_record.activity, HIGHEST_DAILY_ACTIVITY)
                        self.assertLessEqual(act_record.localId, HIGHEST_COW_ID)
                        years = ["2019", "2020"]
                        obs_year = act_record.observationTime.split('-')[0]
                        self.assertIn(obs_year, years)

                    # Check that the filename is initialized properly.
                    filename = Path(full_path).name
                    self.assertEqual(filename, entry.vendorThree.filename)
