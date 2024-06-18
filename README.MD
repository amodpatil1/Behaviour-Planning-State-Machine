:bulb: Maintainer `AMOD PATIL'
## Component Description
Behaviour Planning is state machine which helps the Ego Vehicle to change states based on the situations and types of inputs it receives. The behaviour planning has 5 states Idle, Drive, Stop when a obstacle is detected, Stop near the parking, Park. The Ego vehicle is in idle state where it receives the 'vi_start' trigger from the adapt_vi from which it transition into drive state which has 3 outcomes first is Drive, second is Stop near parking spot, third is Stop when a obstacle is detected. The Drive outcome is achieved when the adapt_roucomp has published a 'route'. Once Ego-vehicle is driving if the adapt_envmod publishes the 'stop' the Ego-vehicle will transition into the Stop when a obstacle is detected. Once the Ego-vehicle has reached the location near the parking spot which is calculated using the current pose which is received from adapt_loc and the goal pose of the path which is received from adapt_roucomp. Once the Ego Vehicle is at the goal pose of the route Park state is triggered where adapt_trajp is set to choose the Park trajectory to park the vehicle. Once the vehicle is parked it returns to idle state.

State 1: Idle

| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /vi_start|string| Start trigger to transition into Drive State | |
| Output |/route|PoseArray| A optimum route from the vehicle's location to the parking spot |

State 2: Drive

| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /route|PoseArray| A optimum route from the vehicle's location to the parking spot | |
| Input |/stop| Bool|This message is published when the node detects obstacle in its close range(forward) | |
| Input |/loc_pose |PoseStamped|Location of Ego Vehicle | |

State 3: Stop when a obstacle is detected

| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /stop|Bool| This message is published when the node detects obstacle in its close range(forward) | |
| Output ||Idle|

State 4: Stop near the parking spot

| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /route|PoseArray| A optimum route from the vehicle's location to the parking spot | |
| Input |/loc_pose |PoseStamped|Location of Ego Vehicle | |
| Output ||Idle|

State 5: Park

| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /traj_trigger|PoseArray| A optimum route from the vehicle's location to the parking spot | |
| Input |/loc_pose |PoseStamped|Location of Ego Vehicle | |
| Output ||Parked|


## The RQT Graph

<img src="images/behpl.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="1810" height="415">

## Behaviour Planning Block Diagram

 <img src="https://git.hs-coburg.de/ADAPT/adapt_behplan/raw/branch/main/images/behplan.jpg" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="850" height="850">



 ## Dependencies
 1. adapt_roucomp
 2. adapt_loc
 3. adapt_envmod
 4. adapt_vi
 5. adapt_trajp
 6. yasmin: https://github.com/uleroboticsgroup/yasmin
 (Note: Please install yasmin on your system before running behaviour planning node)


 ## Installation Instructions

To install the Behaviour Planning package, do follow the steps below:

### Step 1: Create a worksapce

Open the terminal, navigate to the worksapce and create a 'src' directory where you want to clone the repository. 

```shell
mkdir src
```
### Step 2: Clone the Repository
Navigate to 'src' and follow the given command to clone the repository.
```shell
git clone https://git.hs-coburg.de/ADAPT/adapt_behplan.git
```
### Step 3: Build the Package
After cloning the repository, navigate back to the workspace
```shell
cd ..
```
Now, build the package using **`colcon`**:
```shell
colcon build --symlink-install
```
### Step 4: Source the setup file
Once the build is complete, you'll need to source the workspace to make it available to ROS2:
```shell
source install/setup.bash
```
### Step 5: Run the Node
before you run the node make sure to start the adapt_roucomp and adapt_loc components
You can now launch the Behaviour Planning node:
The entry point for Behaviour Planning is **`behstate`**.
```shell
ros2 run adapt_behplan behstate
