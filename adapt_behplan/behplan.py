import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist





class Behplan(Node):

    def __init__(self):
        super().__init__('beh_plan')
        
        
        #Publisher setup
        self.publisher_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0


        #Subscriber setup
        self.subscription = self.create_subscription(Path,'/route',self.route_computer_callback,10)
        self.subscription = self.create_subscription(OccupancyGrid,'/complete_model',self.env_mod_callback,10)
        self.subscription = self.create_subscription(Pose, '/loc_pose',self.localization_callback,10)
   

    def timer_callback(self):
        twist_msg = Twist()
        twist_msg.linear.x = 1.0  #sets the longitudinal velocity 
        twist_msg.angular.z = 0.5 #sets the angular velocity 
        self.publisher_cmd_vel.publish(twist_msg)

        self.get_logger().info('Publishing manouver commmands Linear Velocity: %f, Angular Velocity: %f' % (twist_msg.linear.x, twist_msg.angular.z))
        self.i += 1


    def route_computer_callback(self, msg):
        self.get_logger().info('route: "%s"' %msg.data)
    def env_mod_callback(self, msg):    
        self.get_logger().info('complete_model: "%s"' %msg.data)
    def localization_callback(self, msg):       
        self.get_logger().info('loc_pose: "%s"' %msg.data)

    
def main(args=None):
    rclpy.init(args=args)

    beh_plan = Behplan()

    rclpy.spin(beh_plan)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    beh_plan.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__': 
    main()