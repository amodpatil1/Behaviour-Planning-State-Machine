Behaviour Planning is state machine which helps the Ego Vehicle to change states based on the situations and types of inputs it receives. The behaviour planning has 6 states Idle, Drive, Stop when a obstacle is detected, Stop near the parking, Parking and Parked.

*State 1*: **Idle**

| Trigger |Component | Topic Name | Message Type |
| --------- | ---------- | ---------- | ----------- |
| Trigger | adapt_roucomp|/route_start| Bool | | 

**Outcome**: Drive

*State 2*: **Drive**

| Trigger |Component | Topic Name | Message Type | 
| --------- | ---------- | ---------- | ----------- |
| Trigger | adapt_envmod|/stop| Bool | |

**Outcome 1**: Stop when an obstacle is detected.

| Trigger |Component | Topic Name | Message Type | 
| --------- | ---------- | ---------- | ----------- |
| Trigger | adapt_trajp|/reach_goal| Bool | |

**Outcome 2**: Stop near the parking spot.


*State 3*: **Stop when an obstacle is detected**

| Trigger |Component | Topic Name | Message Type | 
| --------- | ---------- | ---------- | ----------- |
| Trigger |  adapt_envmod|/stop| Bool | |

**Outcome**: Stop when an obstacle is detected.

*State 4*: **Stop near the parking spot**

| Trigger |Component | Topic Name | Message Type | 
| --------- | ---------- | ---------- | ----------- |
| Trigger | adapt_trajp|/park| Bool | |

**Outcome**: Parking.

*State 5*: **Parking**

| Inputs/Trigger |Component | Topic Name | Message Type | 
| --------- | ---------- | ---------- | ----------- |
| Trigger | adapt_mobint|/final_state| Bool | |

**Outcome**: Parked.

*State 6*: **Parked**


## Behaviour Planning Block Diagram 
<img src="https://github.com/amodpatil1/Behaviour-Planning-State-Machine/blob/main/images/block_diagram.drawio.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="700" height="250">


## Behaviour Planning State Diagram 
<img src="https://github.com/amodpatil1/Behaviour-Planning-State-Machine/blob/main/images/fina.png" alt="Behaviour Planning State Diagram" title="Behaviour Planning" width="700" height="1500">



## Functionality
The behaviour Planning act as the brain of the Ego-vehicle where it receives several inputs from various components and based on the inputs received it triggers the specific functions. It has 6 States and particular state has their own outcomes.
1. Idle 
2. Drive
3. Stop when an obstacle is detected
4. Stop near the parking spot
5. Parking 
6. Parked


 
**State: Idle**

 The idle state has only one outcome which is drive state. In the idle state, when the /route_state is received as True from the adapt_roucomp, the Ego-vehicle is transition into the Drive State and publishes the /drive topic as True to the adapt_trajp. 


**State: Drive**

The Drive state has two outcomes Stop when an obstacle is detected, Stop near the parking spot. In the Drive state it publishes /drive topic as True to the adapt_trajp. Once the adapt_envmod publishes /stop topic as True the Ego-vehicle transition into Stop when an obstacle is detected State. When the topic /reach_goal is received as True from the adapt_trajp, then the Ego-vehicle transitions into the Stop near Parking Spot State. 


**State: Stop when an obstacle is a detected State.**

The Stop when an obstacle has two outcomes which transition the Ego-vehicle into the Stop when an obstacle is detected state and Drive state. When an obstacle detected in the path of the Ego-vehicle the adapt_envmod publishes a /stop topic as True, then the adapt_behplan publishes /drive topic as False to the adapt_trajp. Once the detected obstacle is removed from the path of the Ego-Vehicle the adapt_envmod publishes /stop topic as False, then the adapt_behplan publishes /drive topic as True to the adapt_trajp. 


**State: Stop near the parking spot.**

The Stop near the Parking spot has one outcome which transition the Ego-vehicle into Parking State. When the Ego-vehicle reaches the goal pose of the '/reach_goal' received as True from the adapt_trajp, the Ego-Vehicle transitions into the Parking State. 


**State: Parking**

The Parking state has two outcomes Stop when an obstacle detected State, Parked State. When an obstacle is detected in the path of the Ego-Vehicle Transition into the Stop when an obstacle State. When the adapt_mobint publishes /final_state topic as True, the Ego-vehicle transition into the Parked State.


**State: Parked**



 ## Dependencies
 1. adapt_roucomp
 2. adapt_envmod
 3. adapt_mobint
 4. adapt_trajp
 5. yasmin: https://github.com/uleroboticsgroup/yasmin
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
The entry point for Behaviour Planning is **`behave`**.
```shell
ros2 run adapt_behplan behave
```

## Visulaization Instructions

`ros2 run yasmin_viewer yasmin_viewer_node`

Go to the given link on the web browser.

http://localhost:5000/
