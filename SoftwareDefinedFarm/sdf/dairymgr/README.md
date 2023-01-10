## Overview  (Updated January 2023)
We have evolved to start using Docker containers for running the
Dairymgr programs. This would enable us to make changes and redeploy new
containers as functionality changes. The containerization is done at the
application level, but the same (running) container can be used to start
the different main programs in separate terminals, either in testing mode
or on the Farm PC.

## Rationale behind the system start
To start the system, we use the *_main_dairymgr.py programs. Importantly,
the programs must be started in a pre-determined order because of their
functionality explained below.

- sensor_main_dairymgr.py is started first because it checks for any new
files in the system.
- compute_main_dairymgr is started second because it needs to register with
the sensor module to be notified of any new files before reading them (through
an RPC call to the sensor module which does the actual reading).

We provide the config_template.json file to give an idea for what type of
configuration the above programs expect. The configurations allows these
scripts/containers to be deployed anywhere as long as they have the correct
IP addresses of the other modules that are needed for communication
with the [aggregator](https://github.coecis.cornell.edu/cida/CIDA/tree/develop/FarmDataServer).
Of course, besides the IP addresses of other modules and the aggregator,
other things that can be specified include the sensors whose updates should
be checked and the preferred name for the snapshot (see snapshot.py
description below).


### Running the code 
`python3 *_main_dairymgr.py -c <path/to/config/file>`

Note that we use python3 (instead of just python) because of the way
the containers are built.


## Other files/directories worth explaining

### snapshot.py
This file keeps track of the latest timestamps for sensor readings. It is also
used to save/load snapshots as the sensor_main_dairymgr progresses/resumes.
This snapshot mechanism allows us to not have to write processed_files.txt as we
previously did (circa 2019/2020).
Now timestamps are used to know when there is a new file for a given sensor.
Of course, eventually we want to migrate this snapshotting to a local or
remote database that can be read regardless of where the main program (sensor
module) is started.

### callback_enum_defs.py
This file contains enum classes that map proto definitions for DairyManager 
to Python-format enums. This simplifies the RPC callback and logging
procedures in the application.

### proto
This directory hosts all the protobof definitions in addition to the generated
\*_pb2.py files that can be imported in actual code.

### base
Hosts the type definitions and macros that are used throughout the process and
utility functions that don't exactly fall under a specific data source.

### utils 
Hosts helper functions like processing args and loading snapshots.

### (old) network
Note that this directory now exists one directory up (../). This is because
it fits the entire SDF project, not just this app (though it began in here).
This directory constitutes the underlying network layer that is used by
the main programs. I :recycle: code from my research group's
[Vegvisir](https://vegvisir.cs.cornell.edu/) project because it has been stable
for months now. Though it is stable, it still contains occasional bugs (see
issue [#115](https://github.coecis.cornell.edu/cida/CIDA/issues/115)
for example) that are hard to replicate and fix.
