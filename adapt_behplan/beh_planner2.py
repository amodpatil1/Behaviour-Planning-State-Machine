import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Vector3, PoseArray, Twist, PoseStamped
import math

class CarBehaviour(Node):

    def __init__(self):
        super().__init__('behaviour_planner')

        # Subscriber setup
        self.subscription_route = self.create_subscription(PoseArray, '/route', self.route_callback, 10)
        self.subscription_ang = self.create_subscription(Vector3, '/euler_angles', self.rotation_callback, 10)
        self.subscription_loc = self.create_subscription(PoseStamped, '/loc_pose', self.veh_loc, 10)

        # Publisher setup
        self.cmd_vel = self.create_publisher(Twist, '/cmd_vel', 1)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.twist_callback)


        # Initializing variables
        self.waypoints = []  # Store received waypoints
        self.curr_way_idx = 0  # Index of the current waypoint
        self.reached_parking_spot = False  # Flag to indicate if the parking spot is reached
        self.max_waypoints = 10  # Total number of waypoints
        self.curr_loc = (0.0, 0.0)
        self.curr_yaw = 0.0
        self.dev_angle = 0.0
        self.angular_vel = 0.0
        self.dist_to_stop = 0.0

    def twist_callback(self):
        if self.waypoints and self.reached_parking_spot == False:
            msg = Twist()

            vehicle_stat = self.vicinity_check()
            print(vehicle_stat)

            if self.stop_command(self.dist_to_stop) == True:
                msg.linear.x = 0.00
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))

            if vehicle_stat == 'on_route':
                msg.linear.x = 1.0
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))
                self.cmd_vel.publish(msg)  
            if vehicle_stat == 'off route':
                msg.linear.x = 0.000
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))
            else:    
                msg.linear.x = 0.000
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))
                self.cmd_vel.publish(msg)   

             
        self.waypoint_increment()  
        
    def route_callback(self, msg):

        self.waypoints = msg.poses
        self.get_logger().info('received waypoints')
        self.curr_way_idx = 0

    def veh_loc(self, msg):     
        self.curr_loc = (round(msg.pose.position.x, 4), round(msg.pose.position.y, 4))
        self.get_logger().info('location of vehicle: (%f, %f)' % (self.curr_loc[0], self.curr_loc[1]))

        self.final_loc = (round(msg.pose.position.x, 4), 6.120)
        self.get_logger().info('final destination is : (%f, %f)' % (self.final_loc[0], self.final_loc[1]))
        
        if self.waypoints:
            self.dist_to_stop = math.sqrt((round(self.waypoints[10].position.x, 4) - round(msg.pose.position.x, 4))**2 + 
                                          (round(self.waypoints[10].position.y, 4) - round(msg.pose.position.y, 4))**2)
        
    
    def stop_command(self, close):    
        if 0 < close < 2:
            self.get_logger().info('Stopping the vehicle as it is close to the final destination')
            return True

        else:
            self.get_logger().info('The vehicle is still far from the final destination')
            return False

    def rotation_callback(self, msg):
        
        self.curr_yaw = math.degrees(msg.z)
        self.get_logger().info('yaw angle : %f' % (self.curr_yaw))

    
    def steering_calc(self, curr_yaw):
        target_yaw = 90.0  

        if self.curr_way_idx < len(self.waypoints) - 1:
            self.get_logger().info('Current yaw angle: %f' % (curr_yaw))

            if math.isclose(curr_yaw, target_yaw, abs_tol=2.0):
                self.get_logger().info('Driving straight')
                return 0.0
            
            yaw_difference = abs(target_yaw - curr_yaw)

            if yaw_difference > 2.0:
                self.angular_vel = yaw_difference * 0.3
                self.get_logger().info('Correcting steering angle: %f' % (self.angular_vel))
                return self.angular_vel

            self.get_logger().info('Resetting steering angle to 0.0')
            return 0.0

        self.get_logger().info('No action taken, defaulting to 0.0 angular velocity')
        return 0.0

  
    def vicinity_check(self):
        if 3 < self.curr_loc[0] < 4:
            self.get_logger().info('the vehicle is on track')
            return 'on_route' 
        else:
            self.get_logger().info('the vehicle is off track')
            return 'off route'
        
    def waypoint_increment(self):
        if self.waypoints:
            if self.curr_way_idx == len(self.waypoints)-1:
                self.reached_parking_spot = True

            else:
                if self.curr_loc[1] < self.waypoints[self.curr_way_idx + 1].position.y:
                    self.get_logger().info('the vehicle is approaching the next waypoint')
  
                elif self.curr_loc[1] >= self.waypoints[self.curr_way_idx + 1].position.y:
                    self.get_logger().info('the waypoint (%f,%f) has been reached' % (self.waypoints[self.curr_way_idx + 1].position.x,
                                                                             self.waypoints[self.curr_way_idx + 1].position.y))
                    self.curr_way_idx += 1
                    print(self.curr_way_idx)
                else:
                    self.get_logger().error('something went wrong')
        

def main(args=None):
    rclpy.init(args=args)
    behaviour_planner = CarBehaviour() 
    rclpy.spin(behaviour_planner)
    behaviour_planner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__': 
    main()
        