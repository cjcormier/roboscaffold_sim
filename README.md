__NOTE: The simulation has been ported to Kotlin and this repository is 
deprecated.__

Originally there was going to be support for running the kotlin simulation 
via this UI, but the UI was ported to JavaFX/TornadoFX. 
Thus some of the functionality hinted at by the UI is non-functional 
(namely drawing the structure and changing simulation language, these 
options are left for posterity).

#Overview
This is the repository for the simulation of the 2017-2018 Robotic 
Scaffolding Major Qualifying Project (MQP) at WPI.

## Brief MQP Explaination
The goal Robotic Scaffolding MQP is attempt to create a system that allows 
for autonomous creations of two dimensional structures out of building 
material. This is done by two sub-systems, the scaffolding network and the 
builder robot, working together. 

The scaffolding network is composed of blocks that all connected via other 
scaffolding blocks. The scaffolding blocks can communicate to all other 
connected blocks, in the physical demo this is achieved via a CAN bus. The
scaffolding blocks can also talk to the a builder robot that is directly 
above it. This is achieved via changing an LED on the top face of the block.
The scaffolding blocks have no actuation in of themselves.

The builder robots drive around on top of the the scaffolding network,
receiving instructions from the scaffolding blocks below it. These 
instructions tell the robot where to drive and which blocks (scaffolding or 
building) to pick up and where to place them. The builder robot is assumed
to have no concept of its location and can only hold a single block of any 
type. (While there is some error checking using the held block, this is to 
help debug different algorithms and should not be used in the algorithms 
themselves).

These two systems work together to place building blocks in the shape of the 
target.

#Requirements
The simulation requires python version 3.6 or higher and tk/tcl version 8.5 or higher installed. 
To see if the correct version of tk is installed run tk_check.py. If the wrong version is installed,
follow the instructions [here](http://www.tkdocs.com/tutorial/install.html).

#Applications and Tests
There are two applications in this project, the 
basic_simulation_visualizer.py and strategy_profiling.py applications.
Both of these applications are in the root folder of this project.

__NOTE__: All applications and tests must be started from the project root folder,
otherwise the libraries will not be found correctly. (For example to run
test create_point_test.py", run "python3.6 
roboscaffold_som/tests/create_point.py).

##basic_simulation_visualier.py
This is the main application for this project. The application consists of 
two views: the creation views and the simulation view. 

### Creation View
The creation view allows for specifying the target structure for the 
simulation. There are currently three ways to specify a structure: choosing 
a pre-made structure, choosing a dimension-value pair, and loading a file. 
The ability to create a structure block by block was planned but was not 
implemented before porting the project.

The creation view allows for saving the defined structure and running the 
simulation in the same window or a new one. When running the simulation, 
one of multiple strategies can be selected. The strategies are all variations
of the same basic strategy, but with various vertical offsets.


### Creating a structure using Dimension-Value pairs 
For any specified size there are multiple ways to number the possible 
structures. The simplest way is to number them in binary with each digit
representing whether a coordinate is in structure or not. The method 
used here is similar but requires a block to exist in the first row and 
column this is to reduce repetition. Currently it is not possible to see
the max value for the given dimension in the creation view as this feature 
was not added before the port.

## Simulation View
The simulation view allows the user the run the simulation step by step, or
play it at the given frames per second (FPS). Only the first 1000 frames are 
loaded initially, but more can be load after. Statistics about the currently 
loaded frames are also availible, as well as the ability to save the run.

## strategy_profiling.py
This application tests several strategies and determines which are better 
according to different metrics. The strategies tested are the Basic Spine,
Offset Spine, Centroid, and Longest Spine Strategies. These strategies 
are run on all valid structures of that fit in a square (the dimension
of which can be set in the file). 

There are two metrics that the strategies are tested on the number of robot
moves and number of scaffolding updates. The number of robot moves is more 
impactful as it takes much more time for a robot to more than the 
scaffolding to update.

__NOTE__: Be aware that the runtime of strategy profiling is O(2^(n^2))
where n is the dimension of the square because of the number of possible 
structures. Due to this, it is not recommended to run it for more than a
dimension size of 5 (which may take several hours).