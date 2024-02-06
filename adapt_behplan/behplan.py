import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped,PoseArray, Twist
from geometry_msgs.msg import PoseStamped,PoseArray, Twist





class Behplan(Node):

    def __init__(self):
        super().__init__('beh_plan')
        
        
        #Publisher setup
        self.publisher_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0


        #Subscriber setup
        self.subscription = self.create_subscription(PoseArray,'/route',self.route_computer_callback,10)
        self.subscription = self.create_subscription(OccupancyGrid,'/complete_model',self.env_mod_callback,10)
        self.subscription = self.create_subscription(PoseStamped, '/loc_pose',self.localization_callback,10)
   

    def timer_callback(self):
        twist_msg = Twist()
        twist_msg.linear.x = 1.0  #sets the longitudinal velocity 
        twist_msg.angular.z = 0.5 #sets the angular velocity 
        self.publisher_cmd_vel.publish(twist_msg)

        self.get_logger().info('Publishing manouver commmands Linear Velocity: %f, Angular Velocity: %f' % (twist_msg.linear.x, twist_msg.angular.z))
        self.i += 1


    def route_computer_callback(self, msg):
        poses = msg.poses  # Assuming PoseArray has a 'poses' attribute containing a list of Pose messages

        # Process each pose in the received PoseArray
        for i, pose in enumerate(poses):
            # Access pose information (position and orientation)
            position = pose.position
            orientation = pose.orientation
            self.get_logger().info(f'Pose {i + 1} - Position: ({position.x}, {position.y}, {position.z})'% PoseArray)



    def env_mod_callback(self, msg):    
        self.get_logger().info('complete_model: "%s"' %msg.data)
        self.environment_model = OccupancyGrid()
        self.environment_model.header.frame_id = 'environment_model'
        self.environment_model.info.resolution = 0.5  
        self.environment_model.info.width = 100  # grid size
        self.environment_model.info.height = 100  #grid size
        self.environment_model.data = [0] * (self.environment_model.info.width * self.environment_model.info.height)


    def localization_callback(self, msg,PoseStamped):       
        self.environment_model = OccupancyGrid()
        self.environment_model.header.frame_id = 'environment_model'
        self.environment_model.info.resolution = 0.5  
        self.environment_model.info.width = 100  # grid size
        self.environment_model.info.height = 100  #grid size
        self.environment_model.data = [0] * (self.environment_model.info.width * self.environment_model.info.height)


    def localization_callback(self, msg,PoseStamped):       
        self.get_logger().info('loc_pose: "%s"' %msg.data)
        self.localization.header.frame_id = 'localization'

        self.localization.header.frame_id = 'localization'


    
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
