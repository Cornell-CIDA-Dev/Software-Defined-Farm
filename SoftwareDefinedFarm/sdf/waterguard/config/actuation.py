# System imports
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# A class for configuring waterguard Twilio actuation.
class WaterGuardActuationConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the authentication token,
                          operator number, etc.
        """
        super().__init__(config)

        # Configure all the module IP addresses (if any)
        self.account_sid = config['accountSID']
        self.auth_token = config['authToken']
        self.twilio_num = config['twilioNum']
        self.operator_num = config['operatorNum']
