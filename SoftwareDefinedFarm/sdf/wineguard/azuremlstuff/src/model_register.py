import sys, getopt
from os.path import exists
import json
from pathlib import Path
from azureml.core import Dataset, Run, Workspace
from sdf.wineguard.modelmanagement.model_funcs import register_model


def azure_register_model(pk_rfm_filepath, **kwargs) :
    # let the pickled RFm be filename
    rfm_name = Path(pk_rfm_filepath).stem

    sub_id = kwargs['sub_id']
    resource_group = kwargs['resource_group']
    workspace_name = kwargs['workspace_name']

    azure_ws = Workspace(sub_id, resource_group, workspace_name)
    #push rfm
    # TO-DO: pass JSON with RFm tags, name, filepath as sys arg
    # DELETE ME - temp dict.

    rfm_dict = {
            "Correction1":"BRDF",
            "Correction2":"Topographic Corrections",
            "Correction3":"Vector Normalized",
            "Data":"Spectral Mixture Residual",
            "Python_Version":"Python 3.8"
            }

    rfm_description = "RF model for Grapevine Leafroll Virus Complex, California Lodi"

    register_model(pk_rfm_filepath, rfm_name, rfm_dict, rfm_description, azure_ws)


def main(argv) :
    '''Takes in a json file with Azure registration parameters
    '''
    long_input = ["--help","--azure_file", "--Pickled_RFm"]
    short_input = "hf:p:"

    asked_for_help = False
    azure_file = None
    pRFm_file = ''

    try :
        options, current_values = getopt.getopt(argv, short_input, long_input)

        for option, current_value in options :
            if option in ("-h","--help") :
                print("model_register.py -f <filepath to azure parameters> -p <filepath to pickled random forest model>")
                asked_for_help = True
            elif option in ("-f", "--azure_file") :
                azure_file = current_value
            elif option in ("-p", "--Pickled_RFm") :
                pRFm_file = current_value

    except getopt.GetoptError as e :
        print(">>> ERROR: %s" % str(e))

    if not asked_for_help :
        with open(azure_file) as af :
            azure_params = json.load(af)
            azure_register_model(pRFm_file, **azure_params)


if __name__ == '__main__' :
    main(sys.argv[1:])
