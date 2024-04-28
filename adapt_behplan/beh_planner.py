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
        self.cmd_vel = self.create_publisher(Twist, '/act_cmd', 10)
        timer_period = 0.025  # seconds
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

    def twist_callback(self):
        if self.waypoints:
            msg = Twist()

            vehicle_stat = self.vicinity_check()
            if vehicle_stat == 'on_route':
                msg.linear.x = 1.0
                msg.angular.z = self.steering_calc()
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.linear.y))
            else:
                msg.linear.x = 0.001
                msg.angular.z = self.steering_calc()
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.linear.y))

    def route_callback(self, msg):
        self.waypoints = msg.poses
        self.get_logger().info('received waypoints')
        self.curr_way_idx = 0

    def veh_loc(self, msg):

        self.curr_loc = (round(msg.pose.position.x, 4), round(msg.pose.position.y, 4))
        self.get_logger().info('location of vehicle: (%f, %f)' % (self.curr_loc[0], self.curr_loc[1]))

        self.final_loc = (round(msg.pose.position.x, 4), 6.120)
        self.get_logger().info('final destination is : (%f, %f)' % (self.final_loc[0], self.final_loc[1]))

    def rotation_callback(self, msg):
        self.curr_yaw = math.degrees(msg.z)
        self.get_logger().info('yaw angle : %f' % (self.curr_yaw))

    def steering_calc(self):
        if self.curr_way_idx < len(self.waypoints):

            self.next_waypoint = (self.waypoints[self.curr_way_idx + 1].position.x, self.waypoints[self.curr_way_idx + 1].position.y)

            if self.curr_yaw == -90:
                self.get_logger().info('no deviation')

            else:   
                if 0 < self.curr_yaw < -90:
                    self.dev_angle = 90 - abs(self.curr_yaw)
                    self.angular_vel =  float(self.dev_angle * 0.23)
                    self.get_logger().info('steering angle: %f' % (self.angular_vel))

                if -90 < self.curr_yaw < -180:
                    self.dev_angle = abs(self.curr_yaw) - 90
                    self.angular_vel = float(-self.dev_angle * 0.23)
                    self.get_logger().info('steering angle: %f' % (self.angular_vel))

        return self.angular_vel      
  
    def vicinity_check(self):
        if 3 < self.curr_loc[0] < 4:
            return 'on_route' 
        else:
            return 'off route'
        
    def waypoint_increment(self):

        if self.curr_loc[1] < self.waypoints[self.curr_way_idx + 1].position.y:
           self.get_logger().info('the vehicle is approaching the next waypoint')
  
        elif self.curr_loc[1] >= self.waypoints[self.curr_way_idx + 1].position.y:
             self.get_logger().info('the waypoint (%f,%f) has been reached' % (self.waypoints[self.curr_way_idx + 1].position.x,
                                                                             self.waypoints[self.curr_way_idx + 1].position.y))
             self.curr_way_idx += 1
             return self.curr_way_idx
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
        