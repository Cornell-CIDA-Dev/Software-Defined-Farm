from sdf.dairymgr.vendorone.milk_yield_processor import MilkYieldReader 


import factory


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class MilkYieldFactory(factory.Factory):
    class Meta:
        model = MilkYieldReader 
