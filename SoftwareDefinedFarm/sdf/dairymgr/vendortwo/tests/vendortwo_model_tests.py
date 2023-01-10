import unittest
import inspect
from pathlib import Path


from sdf.dairymgr.base.spreadsheet_utils import get_value
from sdf.dairymgr.base.global_defs import Casts
from sdf.dairymgr.vendortwo.tests import processor_factories as p_factories


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# @brief: A class for testing the prediction data processor.
class TestPredictionProcessorClass(unittest.TestCase):

    def test_get_value(self):
        """ Test the get_value method using basic data types. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        row = {'NMAST' : 3, 'PEN': "5", 'FDAT': "01/06/2019"}
        prediction_processor = p_factories.PredictionFactory()

        # Test casting to string
        nmast = get_value(row, 'NMAST', "bogusfile.txt", casting=Casts.STR)
        self.assertEqual("3", nmast) 

        # Test casting to int
        pen = get_value(row, 'PEN', "bogusfile.txt", casting=Casts.INT)
        self.assertIsInstance(pen, int)


    def test_read(self):
        """ Test the read method using a prediction data file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        prediction_processor = p_factories.PredictionFactory()
        file_path = "vendortwo_test_data/prediction/cowspre_01072020_0112.csv"
        entries = prediction_processor.read(file_path)

        # Check individual messages for key fields and messages.
        count = 0

        for entry in entries:

            self.assertGreaterEqual(len(entry.vendorTwo.prediction.allPredEntries), 1)
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorTwo.filename)

            for pred_msg in entry.vendorTwo.prediction.allPredEntries:
                self.assertTrue(pred_msg.key.id)
                self.assertTrue(pred_msg.key.pen)
                self.assertTrue(pred_msg.fdat)
                self.assertTrue(pred_msg.dim)
                if count < 3:
                    self.assertLess(pred_msg.key.id, 2600)
                count += 1

        # Check that the abscence of a file is raised as an exception.
        bogus_file_path = "vendortwo_test_data/prediction/cowspre_01072020_0115.csv"
        self.assertRaises(FileNotFoundError, prediction_processor.read,
                          bogus_file_path)
           
        
# @brief: A class for testing the fresh feature data processor.
class TestFeatureProcessorClass(unittest.TestCase):

    def test_read(self):
        """ Test the read method using a fresh feature test file. """

        print("Test running: %s\n" % inspect.stack()[0][3])
        feature_processor = p_factories.FreshFeatureFactory()


        # Check that file processing goes smoothly.
        file_path = "vendortwo_test_data/freshfeatures/frshlst_01072020_0102.csv"
        entries = feature_processor.read(file_path)

        # Check individual fields in messages.
        for entry in entries:

            self.assertGreaterEqual(len(entry.vendorTwo.fresh_features.allFreshEntries),
                                    1)
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorTwo.filename)

            for fresh_feat_msg in entry.vendorTwo.fresh_features.allFreshEntries:
                self.assertTrue(fresh_feat_msg.key.id)
                self.assertTrue(fresh_feat_msg.key.lact)
                self.assertTrue(fresh_feat_msg.fdat)
                self.assertTrue(fresh_feat_msg.afcda) 
                self.assertTrue(fresh_feat_msg.mosfh) 
                self.assertFalse(fresh_feat_msg.calving.deadc)
                self.assertFalse(fresh_feat_msg.calving.casex)

                # Check that the right types are being returned.
                self.assertIsInstance(fresh_feat_msg.calving.cadoa, int)
                self.assertIsInstance(fresh_feat_msg.lactData.pdmi, int)
                self.assertIsInstance(fresh_feat_msg.gestation.prefr, int)
                self.assertIsInstance(fresh_feat_msg.gestation.ddry, int)
                self.assertIsInstance(fresh_feat_msg.gestation.cint, int)
                self.assertIsInstance(fresh_feat_msg.gestation.pdcc, int)
                self.assertIsInstance(fresh_feat_msg.gestation.blues, bool)


# @brief: A class for testing the historical data processor.
class TestHistoricalProcessorClass(unittest.TestCase):

    def test_read(self):
        """ Test the read method using a fresh feature test file. """

        print("Test running %s\n" % inspect.stack()[0][3])
        historical_processor = p_factories.HistoricalFactory() 


        # Check that file processing goes smoothly.
        file_path = "vendortwo_test_data/historical/01_03_20.xlsx"
        entries = historical_processor.read(file_path)

        # Check individual fields in messages.
        for entry in entries:

            self.assertEqual(len(entry.vendorTwo.historical.allHistEntries), 33)
            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorTwo.filename)

            for hist_msg in entry.vendorTwo.historical.allHistEntries:
                self.assertGreater(hist_msg.key.id, 0)
                self.assertFalse(hist_msg.key.lact)
                self.assertEqual(hist_msg.key.pen, 13)
                self.assertFalse(hist_msg.mosfh)
                self.assertFalse(hist_msg.calving.deadc)
                self.assertFalse(hist_msg.calving.casex)
                self.assertFalse(hist_msg.calving.cadoa)
                self.assertFalse(hist_msg.calving.ddat)
                self.assertEqual(hist_msg.gestation.cu, "2020-01-03 00:00:00")

                # The next three fields (totm, totf, totp) are all zeroes.

                # Testing values and types
                # These should catch any changes to the test/proto file.
                self.assertLessEqual(hist_msg.tbrd, 7)
                self.assertFalse(hist_msg.mastitisEvents.mtt30)
                self.assertFalse(hist_msg.mastitisEvents.mt030)
                self.assertLessEqual(hist_msg.lameEvents.nlame, 2)
                self.assertLessEqual(hist_msg.lameEvents.lmn30, 2)
                self.assertFalse(hist_msg.lameEvents.lm030)
                self.assertIsInstance(hist_msg.specificHealthEvents.trp,
                                      int)
                self.assertIsInstance(hist_msg.specificHealthEvents.tmet,
                                      int)
                self.assertIsInstance(hist_msg.specificHealthEvents.da030,
                                      int)
                self.assertIsInstance(
                               hist_msg.specificHealthEvents.da30,
                                      int)

                # Test that tbrd is an integer.
                self.assertIsInstance(hist_msg.tbrd, int)


# @brief: A class for testing the pencap data processor.
class TestPencapProcessorClass(unittest.TestCase):

    def test_read(self):
        """ Test the read method using a fresh feature test file. """

        print("Test running %s\n" % inspect.stack()[0][3])
        pencap_processor = p_factories.PenCapFactory() 

        # Check that file processing goes smoothly.
        file_path = "vendortwo_test_data/pencap/pencap_01062020_1111.csv"
        entries = pencap_processor.read(file_path)

        # Check that the right values are being returned.
        for entry in entries:

            filename = Path(file_path).name
            self.assertEqual(filename, entry.vendorTwo.filename)

            count = 0
            for pencap_msg in entry.vendorTwo.pen_cap.all_pens:
                self.assertTrue(pencap_msg.byPen)
                self.assertTrue(pencap_msg.avPencp)
                self.assertLessEqual(pencap_msg.avPencp, 201)

                if count < 6:
                    self.assertLess(pencap_msg.byPen, 10)
                count += 1

                # Check that the right types are being returned.
                self.assertIsInstance(pencap_msg.byPen, int)
                self.assertIsInstance(pencap_msg.avPencp, int)
            

if __name__ == "__main__":
    unittest.main()        
