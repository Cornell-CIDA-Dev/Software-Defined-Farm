# System packages


# Local packages
from sdf.dairymgr.vendorthree.hourly_rumination_processor import HourlyRuminationSensor
from sdf.dairymgr.vendorthree.daily_rumination_processor import DailyRuminationSensor
from sdf.dairymgr.vendorthree.activity_processor import ActivitySensor


# Third party packages
import factory


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


class ActivityFactory(factory.Factory):
    class Meta:
        model = ActivitySensor


class HourlyRuminationFactory(factory.Factory):
    class Meta:
        model = HourlyRuminationSensor


class DailyRuminationFactory(factory.Factory):
    class Meta:
        model = DailyRuminationSensor
