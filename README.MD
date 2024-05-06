:bulb: Maintainer `AMOD PATIL & ANISH PATIL`
## Component Description
Behaviour Planning integrates inputs from the Environment Model and Route Computer, determining the vehicle's path, speed, and maneuvers based on the inputs from the Environmental Model which gives the occupancy gridmap and the Route computer which Provides the optimal route towards the parking spot. After computing all the inputs, Behviour Planning outputs speed limits and maneuver commands in the form of a Twist message, which are executed by the Lateral and Longitudinal Control systems.
| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /route|PoseArray| A optimum route from the vehicle's location to the parking spot | |
| Input |/complete_model |OccupancyGrid|Complete model of where the vehicle is located with respect to its environment | |
| Input |/loc_pose |PoseStamped|Location of Ego Vehicle | |
| Output |/act_cmd |Twist| linear and angular velocities of the vehicle |

## The RQT Graph

<img src="images/behpl.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="881" height="350">

## Behaviour Planning Block Diagram

 <img src="images/behplan.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="611" height="241">

 ## Functionality
 The behaviour planning node need three inputs to run which are described below, without these topics the node will not run.:
 1. Waypoints from the /route Topic
 2. Vehicle location from the /loc_pose topic 
 3. Rotation of the vehicle (yaw) from the /euler_angles topic

 The functions are as follows:
 1. The veh_loc() function subscribes the vehicle's current location and the final location 
 where the car needs to head (for now we have hard coded it as we were not using spot selector Component)
 and store it a variable. This function also calculates the distance between the current location and the final location to use it as required further
 in the Node.
 2. The route_callback() function subscribes to the PoseArray message from /route topic to store all the data as a array to be used later. the route_callback()
 necessary to make behaviour planning run.
 3. Stop_command() returns a bool based on whether or not the car is close the destination.
 4. Rotation_callback() it converts radian yaw into degrees to be processed further.
 5. Steering_calc() it calculates the angular velocity so as to keep the vehicle on track since the default steering diverts the vehicle away from
 its trajectory.
 6. Vicinity_check() returns a bool based on whether the car is on the desired lane or not
 7. Waypoint_increment() this function takes care that after the vehicle crosses the next waypoint it increments the already set self.curr_way_idx = 0 to 1
 so it helps the vehicle to know when to stop.

 ## Dependencies
 1. adapt_roucomp
 2. adapt_loc

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
The entry point for Behaviour Planning is **`planner`**.
```shell
ros2 run adapt_behplan planner
