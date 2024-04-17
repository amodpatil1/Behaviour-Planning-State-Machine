import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, PoseArray, Twist
import math

class Behplan(Node):

    def __init__(self):
        super().__init__('beh_plan')

        # Publisher setup
        self.publisher_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Subscriber setup
        self.subscription_route = self.create_subscription(PoseArray, '/route', self.route_computer_callback, 10)
        self.subscription_model = self.create_subscription(OccupancyGrid, '/complete_model', self.env_mod_callback, 10)
        self.subscription_loc = self.create_subscription(PoseStamped, '/loc_pose', self.localization_callback, 10)

        # Initializing variables
        self.waypoints = []  # Store received waypoints
        self.current_waypoint_index = 0  # Index of the current waypoint
        self.reached_parking_spot = False  # Flag to indicate if the parking spot is reached
        self.max_waypoints = 10  # Total number of waypoints

    def timer_callback(self):
        twist_msg = Twist()
        
        if not self.waypoints:
            return  # No waypoints received yet
        
        if self.reached_parking_spot:
            twist_msg.linear.x = 0.0  # Stop the vehicle
        else:
            if self.current_waypoint_index <= 4:
                twist_msg.linear.x = (self.current_waypoint_index + 1) * 0.1  # Accelerate
            else:
                # Decelerate after reaching waypoint 5
                twist_msg.linear.x = max(0.0, 1.0 - (self.current_waypoint_index + 1) * 0.1)

        twist_msg.angular.z = 0.0  # No angular velocity for this example
        self.publisher_cmd_vel.publish(twist_msg)
        self.get_logger().info('Publishing maneuver commands - Linear Velocity: %f, Angular Velocity: %f' % (twist_msg.linear.x, twist_msg.angular.z))

    def route_computer_callback(self, msg):
        self.waypoints = msg.poses  # Store received waypoints
        self.current_waypoint_index = 0  # Reset waypoint index
        self.reached_parking_spot = False  # Reset parking spot flag

    def env_mod_callback(self, msg):    
        # Process environment model data if needed
        pass

    def localization_callback(self, msg: PoseStamped):
        if self.waypoints:
            # Check distance to the current waypoint
            if self.current_waypoint_index == self.max_waypoints - 1:
                        self.reached_parking_spot = True  

            else:
                current_waypoint = (msg.pose.position.x, msg.pose.position.y)
                next_waypoint = (self.waypoints[self.current_waypoint_index + 1].position.x, self.waypoints[self.current_waypoint_index + 1].position.y)
                distance_to_waypoint = math.sqrt((next_waypoint[0] - current_waypoint[0]) ** 2 + (next_waypoint[1] - current_waypoint[1]) ** 2)
                

                if 0.0 < distance_to_waypoint < 0.1:  # Assuming 0.1 is a threshold for reaching a waypoint
                    # Check if there are more waypoints
                    self.current_waypoint_index += 1    
                 
           

def main(args=None):
    rclpy.init(args=args)
    beh_plan = Behplan() 
    rclpy.spin(beh_plan)
    beh_plan.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__': 
    main()
