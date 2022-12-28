## Overview  (Updated September 2022)
We use the scripts in this directory to run modules for the WaterGuard
application. These modules can be deployed anywhere as long as each module's
configuration specifies the location of its peer modules (see config) below.

## Rationale behind the system start
To start the system, we use the *_main_dairymgr.py programs. Importantly,
the programs must be started in a pre-determined order because of their
functionality which I explain below.

- storage_main_dairymgr.py is started first because it serves as the
interface to the Azure storage for the WaterGuard sensor box and deployments.
- sensor_main_dairymgr.py is started second because it periodically checks
for any sensor updates for a particular sensor box by interacting with the
storage module.
- actuation_main_dairymgr.py is started third because it receives actuation
signals coming from the compute module before issuing calls to the Twilio
API. 
- compute_main_dairymgr.py is started last because it (1) registers with the
sensor module to receive updates (and configurations) of a certain sensor
box, (2) interacts with the actuation module to send the appropriate action
once the updates it receives from the sensor module reaches certain thresholds.

We provide the config_template_wineguard.json file to give an idea for what type of
configuration the above programs expect. The configurations allows these
scripts/containers to be deployed anywhere as long as they have the correct
IP addresses of the other modules that are needed for communication.


### Running the code 
`python3 *_main_dairymgr.py -c <path/to/config/file>`

Note that we use python3 (instead of just python) because of the way
the containers are built.


## Other files/directories worth explaining

### waterguard*.py
These files are the SDF modules that the main programs rely on to set the
configurations and/or run the modules for WaterGuard.


### callback_enum_defs.py
This file contains enum classes that map proto definitions for WaterGuard
to Python-format enums. This simplifies the RPC callback and logging
procedures in the application.

### config
This directory contains scripts that are imported by each main program
for its configuration purposes. Unliked for dairymgr and wineguard,
we opted to create individual files and a directory because the WaterGuard
application does use all four modules in the API specification. 

### proto 
This directory contains the protobuf definitions that are specific to the
waterguard application. Compared to the farmbios proto that are one directory
up, the proto files in here are more likely to change.
