## Component Description
Behaviour Planning integrates inputs from the Environmental Model and Route Computer, determining the vehicle's path, speed, and maneuvers based on surrounding conditions. It outputs waypoints, speed limits, and maneuver commands, which are executed by the Lateral and Longitudinal Control systems.
| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /route|  nav_msgs/msg/Path| A optimum route from the vehicle's location to the parking spot | |
| Input |/complete_model | |Complete model of where the vehicle is located with respect to its environment | |
| Input |/loc_pose | PoseStamped|Location of Ego Vehicle | |
| Output |/cmd_vel | geometry_msgs/Twist | linear and angular velocities of the vehicle |
## Behaviour Planning Block Diagram
 <img src="images/behplan.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="800" height="250">
