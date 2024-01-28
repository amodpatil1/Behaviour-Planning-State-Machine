## Component Description
Behaviour Planning integrates inputs from the Environmental Model and Route Computer, determining the vehicle's path, speed, and maneuvers based on surrounding conditions. It outputs waypoints, speed limits, and maneuver commands, which are executed by the Lateral and Longitudinal Control systems.
## Component Description
Behaviour Planning integrates inputs from the Environmental Model and Route Computer, determining the vehicle's path, speed, and maneuvers based on surrounding conditions. It outputs waypoints, speed limits, and maneuver commands, which are executed by the Lateral and Longitudinal Control systems.
| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /route|  nav_msgs/msg/Path| A optimum route from the vehicle's location to the parking spot | |
| Input |/complete_model | |Complete model of where the vehicle is located with respect to its environment | |
| Output | /beh_spd | v2x/Speed | Speed specifications of the vehicle | 
| Output | /beh_mcmd |  v2x/LateralAcceleration | Acceleration to the lateral direction |
| **Connected Components** | **Input** - Route Computer, Environment model <br> **Output** - Lateral and Longitudinal Control |
## Behaviour Planning Block Diagram
 <img src="images/behplan.jpg" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="800" height="250">
