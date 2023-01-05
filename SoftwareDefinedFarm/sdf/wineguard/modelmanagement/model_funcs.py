# System imports
from typing import Dict, Any
from joblib import dump
from pickle import load


# Third party imports
from azureml.core import Workspace
from azureml.core import Model

# Local imports


__author__ = "Gloire Rubambiza"
__email__ = "gbr26@cornell.edu"
__credits__ = ["Gloire Rubambiza"]


def dump_model(model, path):
    """
       Dump a trained model into a pickle file to be used later.
       :param model: An object (specify when known)
       :param path: A fully-qualified path where to dump the model.
    """
    try:
        dump(model, path)
    except Exception as ex:
        print("Dumping model failed with exception %s\n" % ex)


def register_model(path: str,
                   name: str,
                   tags: Dict[str, str],
                   description: str,
                   ws: Workspace):
    """
       Register a locally trained model to the cloud.
       :param path: The fully-qualified path to the model pickle file.
       :param name: The name to be given to the model.
       :param tags: Any relevant tags to be associated with the model.
       :param description: A brief description of what the model does.
       :param ws: The Azure ML workspace to be used for registering the model.
    """
    model = Model.register(model_path=path,
                           model_name=name,
                           tags=tags,
                           workspace=ws)
    return model


def get_model(ws: Workspace,
              name: str,
              user_target_dir: str = None,
              replace_if_exist: bool = False):
    """
       Download a pickled model from the cloud.
       :param name: The name to be given to the model.
       :param ws: The Azure ML workspace to be used for getting the model.
       :param user_target_dir: The directory requested by the user for download.
       :param replace_if_exist: Replace the model file/dir if it already
                                exists under the specified directory.
    """
    model_pointer = Model(workspace=ws, name=name)

    # Check if caller specified a directory, otherwise download to current dir
    if user_target_dir != None and replace_if_exist == True:
        model_path = model_pointer.download(target_dir=user_target_dir,
                                      exist_ok=True)
    # The default conditions in the Azure ML workspace re: replacement.
    elif user_target_dir != None and replace_if_exist == False:
        model_path = model_pointer.download(target_dir=user_target_dir)
    else:
        model_path = model_pointer.download(target_dir='.')

    # Load the model and return the un-pickled object
    #with open(model_path, 'rb') as fd:
    #model_object = load(fd)
    #    return model_object


def init():
    global model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'sklearn_regression_model.pkl')
    # Deserialize the model file back into a sklearn model.
    model = joblib.load(model_path)
