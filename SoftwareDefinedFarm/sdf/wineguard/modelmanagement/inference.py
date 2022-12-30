# System imports
from typing import Dict, Any
from joblib import dump


# Third party imports
from azureml.core import Workspace


# Local imports


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]

def init():
    global model
    # AZUREML_MODEL_DIR is an environment variable created during deployment. Join this path with the filename of the model file.
    # It holds the path to the directory that contains the deployed model (./azureml-models/$MODEL_NAME/$VERSION)
    # If there are multiple models, this value is the path to the directory containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv('AZURE_MODEL_DIR'), 'model_name.pkl')
    # Deserialize the model
    model = joblib.load(model_path)


def run(data):
    # Scoring code to be written by Ferg
