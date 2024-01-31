import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BehplanPub(Node):

    def __init__(self):
        super().__init__('beh_plan')
        
        
        #Publisher setup
        self.publisher_spd = self.create_publisher(String, 'beh_spd/spd', 10)
        self.publisher_mc_md = self.create_publisher(String, 'beh_mcmd/mc_md', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0


        #Subscriber setup
        self.subscription = self.create_subscription(String,'/routecomputer/route',self.route_callback,10)
        self.subscription = self.create_subscription(String,'/env_mod/complete_model',self.env_mod_callback,10)
   

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello Team: %d' % self.i
        self.publisher_spd.publish(msg)
        self.publisher_mc_md.publish(msg)
        self.get_logger().info ('Publishing:"/spd" %s' % msg.data)
        self.get_logger().info ('Publishing:"/mc_md" %s' % msg.data)
        self.i += 1

    def route_callback(self, msg):
        self.get_logger().info('route: "%s"' %msg.data)
    def env_mod_callback(self, msg):    
        self.get_logger().info('env_mod: "%s"' %msg.data)

    
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
