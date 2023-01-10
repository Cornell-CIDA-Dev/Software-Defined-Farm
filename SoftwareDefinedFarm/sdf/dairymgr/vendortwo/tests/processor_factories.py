from sdf.dairymgr.vendortwo.prediction_processor import PredictionReader
from sdf.dairymgr.vendortwo.historical_processor import HistoricalReader
from sdf.dairymgr.vendortwo.pencap_processor import PenCapReader
from sdf.dairymgr.vendortwo.feature_processor import FeatureReader
from sdf.network.network_controller import NetworkController 


import factory


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class PredictionFactory(factory.Factory):
    class Meta:
        model = PredictionReader


class HistoricalFactory(factory.Factory):
    class Meta:
        model = HistoricalReader


class FreshFeatureFactory(factory.Factory):
    class Meta:
        model = FeatureReader


class PenCapFactory(factory.Factory):
    class Meta:
        model = PenCapReader


class NetworkControllerFactory(factory.Factory):
    class Meta:
        model = NetworkController
