# System import
from datetime import date
from time import time
from typing import Dict


# Local imports
from sdf.wineguard.proto.wineguard_pb2 import ExperimentSetup


# Azure imports
from azureml.core import (Dataset, Environment, Experiment, ScriptRunConfig,
                          Workspace)
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig


def get_experiment_url(ws: Workspace,
                       specs: ExperimentSetup):
    """
       Submit an experiment and return the associated URL in Azure portal
       :param ws: The workspace to submit the experiment under.
       :param specs: The user specified settings.
       :rtype: A string.
    """
    
    if specs.experimentName != None:
        experiment_name = specs.experimentName 
    else:
        experiment_name = specs.access.workspaceName +  '-' + str(date.today())
        experiment_name += experiment_name +  '-' + str(time())
    
    experiment = Experiment(workspace=ws, name=experiment_name)

    # Set the dataset consumption config to be used
    dataset = Dataset.get_by_name(ws, name=specs.dataset.name)
    dataset_location = None
    if specs.dataset.lookupKey != None:
        dataset_location = dataset.as_named_input(specs.dataset.lookupKey).as_download()
    else:
        dataset_location = dataset.as_download() 
    
    config = ScriptRunConfig(source_directory='./azuremlstuff/src',
                             script=specs.entryScript,
                             arguments=[dataset_location],
                             compute_target=specs.computeCluster)
    
    # Set up the environment from requirements file
    env_setup = specs.env
    if env_setup != None:
        env = Environment.from_pip_requirements(name=env_setup.name,
                                                file_path=env_setup.reqsPath
                                               )
    else:
        env = Environment.from_pip_requirements(
                                                name='randomforest-env',
                              file_path='./azuremlstuff/.azureml/rf_vines_requirements.txt'
                                               )
    config.run_config.environment = env
    
    run = experiment.submit(config)
    return run.get_portal_url()
