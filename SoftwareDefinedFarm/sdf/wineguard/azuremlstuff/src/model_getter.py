import sys, getopt, json
from os.path import exists
from pathlib import Path
from azureml.core import Dataset, Run, Workspace
from sdf.wineguard.modelmanagement.model_funcs import get_model


def azure_get_model(**kwargs) :
    # Azure cloud parameters
    sub_id = kwargs['sub_id']
    resource_group = kwargs['resource_group']
    workspace_name = kwargs['workspace_name']
    # Model specific parameters
    name = kwargs['model_name']
    outputdir = kwargs['outputdir']
    replace = True

    azure_ws = Workspace(sub_id, resource_group, workspace_name)

    get_model(azure_ws, name, outputdir, replace)


def main(argv) :
    '''Takes in a json file with Azure registration parameters
    '''
    long_input = ["--help","--azure_file", "--model_name", "--outputdir"]
    short_input = "hf:m:o:"

    asked_for_help = False
    azure_file = None
    model_name = ''
    outputdir = ''

    try :
        options, current_values = getopt.getopt(argv, short_input, long_input)

        for option, current_value in options :
            if option in ("-h","--help") :
                print("model_getter.py -f <filepath to azure parameters> -m <model name> -o <outputdir>")
                asked_for_help = True
            elif option in ("-f", "--azure_file") :
                azure_file = current_value
            elif option in ("-m","--model_name") :
                model_name = current_value
            elif option in ("-o", "--outputdir") :
                outputdir = current_value

    except getopt.GetoptError as e :
        print(">>> ERROR: %s" % str(e))

    if not asked_for_help :
        with open(azure_file) as af :
            azure_params = json.load(af)
            azure_params['model_name'] = model_name
            azure_params['outputdir'] = outputdir
            azure_get_model(**azure_params)


if __name__ == '__main__' :
    main(sys.argv[1:])
