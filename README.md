This is the repository for the simulation of the 2017-2018 Robotic Scaffolding MQP at WPI.

The simulation requires python version 3.6 or higher and tk/tcl version 8.5 or higher installed. 
To see if the correct version of tk is installed run tk_check.py. If the wrong version is installed,
follow the instructions [here](http://www.tkdocs.com/tutorial/install.html).

The python files in the top level folder are demos for the current version of the simulation.

Each test has one prefix:

|Prefix|Meaning|
|---|---|
|tk |test the UI|
|move |tests the builder movement capabilities of the simulation|
|create |runs the full simulation on a pre-determined structure|