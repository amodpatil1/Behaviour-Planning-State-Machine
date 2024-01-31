import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Twist





class BehplanPub(Node):

    def __init__(self):
        super().__init__('beh_plan')
        
        
        #Publisher setup
        self.publisher_cmd_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0


        #Subscriber setup
<<<<<<< HEAD
        self.subscription = self.create_subscription(Path,'/routecomputer/route',self.route_callback,10)
        self.subscription = self.create_subscription(OccupancyGrid,'/env_mod/complete_model',self.env_mod_callback,10)
        self.subscription = self.create_subscription(Pose, '/localization/loc_pose',self.localization_callback,10)
=======
        self.subscription = self.create_subscription(String,'/routecomputer/route',self.route_callback,10)
        self.subscription = self.create_subscription(String,'/env_mod/complete_model',self.env_mod_callback,10)
>>>>>>> 5b9016b5dc764349de460aaf5a848de68851257a
   

    def timer_callback(self):
        twist_msg = Twist()
        twist_msg.linear.x = 1.0  
        twist_msg.angular.z = 0.5  

        self.publisher_cmd_vel.publish(twist_msg)

        self.get_logger().info('Publishing manouver commmands Linear Velocity: %f, Angular Velocity: %f' % (twist_msg.linear.x, twist_msg.angular.z))
        self.i += 1


    def route_callback(self, msg):
        self.get_logger().info('route: "%s"' %msg.data)
    def env_mod_callback(self, msg):    
        self.get_logger().info('env_mod: "%s"' %msg.data)
    def localization_callback(self, msg):       
        self.get_logger().info('localization: "%s"' %msg.data)

    
def main(args=None):
    rclpy.init(args=args)

    beh_plan = BehplanPub()

    rclpy.spin(beh_plan)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    beh_plan.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__': 
    main()
