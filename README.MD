## Component Description
Behaviour Planning integrates inputs from the Environmental Model and Route Computer, determining the vehicle's path, speed, and maneuvers based on surrounding conditions. It outputs waypoints, speed limits, and maneuver commands, which are executed by the Lateral and Longitudinal Control systems.
| In/Out | Topic Name| Message Type | Description | 
| --------- | ---------- | ---------- | ----------- |
| Input | /optimal_route| |  |
| Input | /virtual_spatial_time_env|  | |
| Output | /speed| |
| Output | /way_points| | |
| Output | /manouver_commands| | |
## Behaviour Planning Block Diagram
 <img src="images/behav.png" alt="Behaviour Planning Block Diagram" title="Behaviour Planning" width="800" height="250">
