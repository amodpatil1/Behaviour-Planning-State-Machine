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
        self.act_cmd = self.create_publisher(Twist, '/act_cmd', 5)
        timer_period = 0.025  # seconds
        self.timer = self.create_timer(timer_period, self.twist_callback)


        # Initializing variables
        self.waypoints = []                                                                     # Store received waypoints
        self.curr_way_idx = 0                                                                   # Index of the current waypoint
        self.reached_parking_spot = False                                                       # Flag to indicate if the parking spot is reached
        self.max_waypoints = 10                                                                 # Total number of waypoints
        self.curr_loc = (0.0, 0.0)                                                              # Initialise current location variable
        self.curr_yaw = 0.0                                                                     # Initialise current yaw variable
        self.dev_angle = 0.0                                                                    # Initialise deviation angle variable
        self.angular_vel = 0.0                                                                  # Initialise angular_vel variable
        self.dist_to_stop = 0.0                                                                 # Initialise distance to stop variable

    def twist_callback(self):

        #the twist callback publishes the topic /cmd_vel to communicate with the motor via CAN BUS
        #the function will only work if the waypoints are received and the car has not reached the destination
        if self.waypoints and self.reached_parking_spot == False:
            msg = Twist()

            vehicle_stat = self.vicinity_check()
            print(vehicle_stat)

            # the following condition calls the self.stop_command function to check whether the car is near the destination or not
            #if it is it stops the car
            if self.stop_command(self.dist_to_stop) == True:
                msg.linear.x = 0.00
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))
                self.get_logger().error('first if')

            # the following condition checks the vicity check and stop command and sets the linear velocity to 1 and also the steering calc function is called
            #for the angular.z velocity
            if vehicle_stat == 'on_route' and self.stop_command(self.dist_to_stop) == False:
                msg.linear.x = 1.0
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z)) 
                self.get_logger().error('second if')

            # the following condition checks and if it is off route it stops the car
            if vehicle_stat == 'off route':
                msg.linear.x = 0.000
                msg.angular.z = float(self.steering_calc(self.curr_yaw))
                self.get_logger().info('linear vel: %f, angular vel: %f' % (msg.linear.x, msg.angular.z))
                self.get_logger().error('third if')
            self.cmd_vel.publish(msg)

        #call the function to incremet the waypoint after the car crosses the next waypoint      
        self.waypoint_increment()   
        
    def route_callback(self, msg):
 
        #this function stores the waypoints received and set self.curr_idx to 0
        self.waypoints = msg.poses
        self.get_logger().info('received waypoints')
        self.curr_way_idx = 0

    def veh_loc(self, msg): 

        #this function stores the current location of the car    
        self.curr_loc = (round(msg.pose.position.x, 4), round(msg.pose.position.y, 4))
        self.get_logger().info('location of vehicle: (%f, %f)' % (self.curr_loc[0], self.curr_loc[1]))

        #here the final destination is set, the y coordinate is hard coded and the x location is set to same as the initial x location because we wanted 
        #to drive the car in a straight line
        self.final_loc = (round(msg.pose.position.x, 4), 6.120)
        self.get_logger().info('final destination is : (%f, %f)' % (self.final_loc[0], self.final_loc[1]))
        
        if self.waypoints:

            #calculate the distance to the destination 
            self.dist_to_stop = math.sqrt((round(self.waypoints[10].position.x, 4) - round(msg.pose.position.x, 4))**2 + 
                                          (round(self.waypoints[10].position.y, 4) - round(msg.pose.position.y, 4))**2)
        
    
    def stop_command(self, close): 
        #this function check the range where the car needs to stop and return a bool   
        if 0 < close < 0.5:
            self.get_logger().info('Stopping the vehicle as it is close to the final destination')
            return True

        else:
            self.get_logger().info('The vehicle is still far from the final destination')
            return False

    def rotation_callback(self, msg):
         
        #this function converts radians into degrees 
        self.curr_yaw = math.degrees(msg.z)
        self.get_logger().info('yaw angle : %f' % (self.curr_yaw))

    def steering_calc(self, curr_yaw):
        #checks whether the current waypoint index is less than the no of waypoints
        if self.curr_way_idx < len(self.waypoints)-1:                                    

            self.get_logger().info('Current yaw angle: %f' % (curr_yaw))

            #checks if yaw is in between the tolerance 0.5 from -90 degrees 
            if math.isclose(curr_yaw, -90.0, abs_tol=0.5):
                self.get_logger().info('no deviation')
                return 0.0 
  
            #calculate right steering according to the orientation
            elif 0.0 > curr_yaw > -90.0:
                self.dev_angle = 90.0 - abs(curr_yaw)
                self.angular_vel =  self.dev_angle * 0.3
                self.get_logger().info('steering angle: %f' % (self.angular_vel))
                return self.angular_vel

            #calculate right steering according to the orientation
            elif -90.0 > curr_yaw > -180.0:
                self.dev_angle = abs(curr_yaw) - 90.0
                self.angular_vel = -self.dev_angle * 0.3
                self.get_logger().info('steering angle: %f' % (self.angular_vel))
                return self.angular_vel   
            
            #default calculation
            self.get_logger().info('No action taken, defaulting to 0.0 angular velocity')
            return 0.0

  
    def vicinity_check(self):

        #this function is used to check whether the car is between (x=3 and x=4) which is our desired route
        if 3 < self.curr_loc[0] < 4:
            self.get_logger().info('the vehicle is on track')
            return 'on_route' 
        else:
            self.get_logger().info('the vehicle is off track')
            return 'off route'
        
    def waypoint_increment(self):

        #this function increments the function by 1 after the vehicle crosses next waypoint
        #since we were moving in a straight line is the direction of the y axis, the func increments according to the y coordinates
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
                    self.get_logger().error('waypoint has been incremented') 
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
        