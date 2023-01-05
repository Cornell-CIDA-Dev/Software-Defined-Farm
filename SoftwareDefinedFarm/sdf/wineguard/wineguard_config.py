# System imports
from typing import Any, Dict


# Local imports
from sdf.config.base_config import BaseConfig
from sdf.wineguard.proto.wineguard_pb2 import (Credentials, Dataset,
                                               Environment, ExperimentSetup)


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


# An abstract class for configuring compute module runs.
class WineGuardComputeConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the subscription ID,
                          resource group, etc. 
        """
        super().__init__(config)

        creds = Credentials(subscriptionId=config['access']['subscriptionID'],
                            resourceGroup=config['access']['resourceGroup'],
                            workspaceName=config['access']['workspaceName']
                            )

        dataset = Dataset(name=config['dataset']['name'],
                          trainingFile=config['dataset']['trainingFile'],
                          lookupKey=config['dataset']['lookupKey']
                         )
        env = Environment(localRun=self.colocation,
                          name=config['env']['name'],
                          reqsPath=config['env']['reqsPath']
                         )
        self.exp_setup = ExperimentSetup(env=env,
                                         access=creds,
                                         dataset=dataset,
                                      computeCluster=config['computeCluster'],
                                         entryScript=config['entryScript']
                                        )

        self.log("\nSub ID: %s \nRG: %s \nWorkspace %s\n"  \
                                                      % (creds.subscriptionId,
                                                         creds.resourceGroup,
                                                         creds.workspaceName))


# An abstract class for configuring training module runs.
class WineGuardTrainerConfig(BaseConfig):

    def __init__(self,
                 config: Dict[str, Any],
                 **kwargs):
        """
           :param config: The user-specified configuration including
                          settings like the subscription ID,
                          resource group, etc. 
        """
        super().__init__(config)

        creds = Credentials(subscriptionId=config['access']['subscriptionID'],
                            resourceGroup=config['access']['resourceGroup'],
                            workspaceName=config['access']['workspaceName']
                            )

        dataset = Dataset(name=config['dataset']['name'],
                          trainingFile=config['dataset']['trainingFile'],
                          lookupKey=config['dataset']['lookupKey']
                         )
        env = Environment(localRun=self.colocation,
                          name=config['env']['name'],
                          reqsPath=config['env']['reqsPath']
                         )
        self.exp_setup = ExperimentSetup(env=env,
                                         access=creds,
                                         dataset=dataset,
                                      computeCluster=config['computeCluster'],
                                         entryScript=config['entryScript']
                                        )

        self.log("\nSub ID: %s \nRG: %s \nWorkspace %s\n"  \
                                                      % (creds.subscriptionId,
                                                         creds.resourceGroup,
                                                         creds.workspaceName))
        # Configure any other module IP addresses (if any)
        self.trainer_address = tuple ([ config['trainerHost'],
                                        int(config['trainerPort'])
                                      ])
