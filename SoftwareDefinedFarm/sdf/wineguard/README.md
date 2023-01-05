## Overview  (Updated September 2022)
We use the scripts in this directory to run experiments for the WineGuard
application, either locally or in the Azure cloud. The ideal is for the
SDF API to be cloud-agnostic so that we can plug-and-play cloud ML
services/modules.

## Rationale behind the system start
To start the system, we use the *_main_dairymgr.py programs. Importantly,
the programs must be started in a pre-determined order because of their
functionality which I explain below.

- compute_main_dairymgr.py is started first because it  receives the
analytics call from the training script.
- trainer_main_dairymgr.py is started second because it
needs a TCP connection to the compute module in order to submit analytics
calls.

We provide the config_template_wineguard.json file to give an idea for what type of
configuration the above programs expect. The configurations allows these
scripts/containers to be deployed anywhere as long as they have the correct
IP addresses of the other modules that are needed for communication.


### Running the code 
`python3 *_main_dairymgr.py -c <path/to/config/file>`

Note that we use python3 (instead of just python) because of the way
the containers are built.


## Other files/directories worth explaining

### wineguard*.py
These files are the SDF modules that the main programs rely on to set the
configurations and/or start the experiments for WineGuard.

### callback_enum_defs.py
This file contains enum classes that map proto definitions for WineGuard
to Python-format enums. This simplifies the RPC callback and logging
procedures in the application.

### azuremlstuff 
This directory contains scripts that are structured according to the Azure
ML framework for submitting experiments. We keep this directory so that it's
possible to use the framework for testing while keeping it under the SDF
package. 

### model\_management 
This directory contains helper scripts that can be used by @fer36 to interact
with the SDF package. The idea is to use this directory as a separator between
core changes in the package and how Ferg's modular code uses it.

### proto 
This directory contains the protobuf definitions that are specific to the
wineguard application. Compared to the farmbios proto that are one directory
up, the proto files in here are more likely to change.
