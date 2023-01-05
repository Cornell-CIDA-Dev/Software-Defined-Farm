# System imports
import traceback
from time import time
import os
import sys


# Third party packages 
from azureml.core import Dataset, Run, Workspace
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix


# ADDITIONAL CODE: get AML run from the current context
run = Run.get_context()

def no_WaterBands(bands):
    non_WaterBands = [[0,197], [207,289], [311,424]]

    bands_f = [] # filtered out water bands
    for i_range in non_WaterBands:
        bands_f.extend(["Band_"+str(band) for band in range(i_range[0],
            i_range[1]+1)]) # extends adds a list ot a list

    return bands_f


def vine_plc(train_feats, train_labels):
    return 1


def vine_rf(train_feats, train_labels):
    grid_param = {
            'n_estimators': [100,200,300,600],
            'criterion': ['gini', 'entropy'],
            'bootstrap':[True, False]
            }

    rf = RandomForestClassifier()
    kfolds = KFold(10, True, 1)

    grid_search = GridSearchCV(estimator=rf, param_grid=grid_param,
            scoring='accuracy', cv=kfolds, n_jobs=-1)

    trained_model = grid_search.fit(train_feats, train_labels)

    return trained_model


#def setup_workspace():
#    '''
#       Set up the workspace configuration for use in ML stuff.
#    '''
#    run.log('Getting workspace....', str(time()))
#
#    subscription_id = 'ed150bce-3150-4fe4-b9e9-557ade4ccef5'
#    resource_group = 'cornellfarmbeatsrg'
#    workspace_name = 'WineGuard'
#    
#    return Workspace(subscription_id, resource_group, workspace_name)


def rf_vines_experiment(training_data: str):
    """
       Conduct a random forest experiment with the given dataset.
    """
    try:
        return main(training_data)
    except:
        print(traceback.print_exc())
        return None
   

def main(data):
    ''' Data holds a (.geojson) file
    Data is expected to have the following fields:
        'Band_X'    - Where x is the index of the band in the raster
        'symptoms'  - Binary yes/no if there is symptom present
    '''
    vineSpec_labeled = gpd.read_file(data)
    bands = no_WaterBands(["Band_"+str(i+1) for i in range(425)])
    features = vineSpec_labeled[bands]
    labels = vineSpec_labeled['symptoms']

    # Below we train RF on an equal number of pixels with symptomatic vines present
    #sy_rows = vineSpec_labeled[vineSpec_labeled['symptoms']=='Sy']
    #sy_count = len(sy_rows)
    #ns_rows = vineSpec_labeled[vineSpec_labeled['symptoms']=='Ns'].sample(sy_count)
    #even_vineSpec = pd.concat([ns_rows, sy_rows])
    #features = even_vineSpec[bands]
    #labels = even_vineSpec['symptoms']

    train_feats, test_feats, train_labels, test_labels = train_test_split(features,labels,test_size=0.3)

    accuracies = []
    kappas = []

    for i in range(1):
        trained_model = vine_rf(train_feats, train_labels)
        pred_labels = trained_model.predict(test_feats)

        # Metrics
        acc_score = accuracy_score(test_labels, pred_labels)
        kappa = cohen_kappa_score(test_labels, pred_labels)
        accuracies.append(acc_score)
        kappas.append(kappa)

        #vineSpec_labeled.to_csv("predicted_"+data)

    acc_pd = pd.DataFrame(accuracies)
    print(acc_pd.describe())
    print('Accuracies ->', accuracies)
    print('Kappas ->\n', kappas)
    return accuracies

if __name__ == '__main__':
   
    details = run.get_details()
    run.log('Details -> ', details)

    # Download the entire dataset (a file for now)
    # The input is the download location
    dataset_download_location = sys.argv[1]

    # dataset_download_location = run.input_datasets['geojson_data']
    run.log('Download location ->', dataset_download_location)

    # Specify the file to use for the experiment
    # training_data = sys.argv[2] 
    #training_data = dataset_input + '/' + training_data

    try:
        main(dataset_download_location)
    except:
        print(traceback.print_exc())
