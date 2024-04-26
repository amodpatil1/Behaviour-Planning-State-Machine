import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, PoseArray, Twist
import math

class Behplan(Node):

    def __init__(self):
        super().__init__('beh_plan')

        # Publisher setup
        self.publisher_cmd_vel = self.create_publisher(Twist, '/act_cmd', 10)
        timer_period = 0.025  # seconds
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
        self.current_location = (0.0, 0.0)

    def timer_callback(self):
        if self.reached_parking_spot == False:
            twist_msg = Twist()
        
            if not self.waypoints:
                return  # No waypoints received yet
        
            final_posex = self.waypoints[10].position.x
            final_posey = self.waypoints[10].position.y
            current_pose_x, current_pose_y = self.current_location

            distance = math.sqrt((final_posex - current_pose_x)**2 + (final_posey - current_pose_y)**2)
            print(distance)
            range = 0.5
        
            if distance <= range: 
                twist_msg.linear.x = 0.0  # Stop the vehicle
                twist_msg.angular.z = 0.3 
                print(self.current_location)
                self.get_logger().info('the vehicle has stopped with speed: %f and steering: %f' % (twist_msg.linear.x, twist_msg.angular.z))

            else:
                if self.current_waypoint_index == 0 and self.current_location == (round(self.waypoints[0].position.x, 4), 
                                                                          round(self.waypoints[0].position.y, 4)):
                    self.get_logger().info('the vehicle is currently not moving')

                else:    
                    if self.current_waypoint_index <= 6:
                        twist_msg.linear.x = 1.5  # Accelerate
                        twist_msg.angular.z = 0.3 
                    else:
                # Decelerate after reaching waypoint 7
                        twist_msg.linear.x = max(0.0, 2.0 - (self.current_waypoint_index) * 0.2)
                        twist_msg.angular.z = 0.3 
                        self.get_logger().info('the vehicle has started to decelerate')

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
            # Check distance to the current waypoin 

            if self.current_waypoint_index == len(self.waypoints) - 1:
                self.get_logger().info('the waypoint has been reach')
                self.reached_parking_spot = True
            else:
                self.current_location = (round(msg.pose.position.x, 4), round(msg.pose.position.y, 4))
                self.next_waypoint = (round(self.waypoints[self.current_waypoint_index + 1].position.x, 4), round(self.waypoints[self.current_waypoint_index + 1].position.y, 4))
                distance_to_waypoint = math.sqrt((self.next_waypoint[0] - self.current_location[0]) ** 2 + (self.next_waypoint[1] - self.current_location[1]) ** 2)
                

                if 0.0 < distance_to_waypoint < 0.15:  # Assuming 0.1 is a threshold for reaching a waypoint
                    # Check if there are more waypoints
                    self.current_waypoint_index += 1  
                    self.get_logger().info('current waypoint index = %d' % (self.current_waypoint_index))
                    self.get_logger().info('the waypoint has been incremented')  
        
def main(args=None):
    rclpy.init(args=args)
    beh_plan = Behplan() 
    rclpy.spin(beh_plan)
    beh_plan.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__': 
    main()
