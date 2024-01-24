import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class Behplan(Node):

    def __init__(self):
        super().__init__('beh_plan')
        self.subscription = self.create_subscription(String,'/routecomputer/route',self.listener_callback,10)
        self.subscription = self.create_subscription(String,'/complete_model/env_mod',self.listener_callback,10)

    def listener_callback(self, msg):
        self.get_logger().info('Route: "%s"' % msg.data)

    def listener_callback(self, msg):
        self.get_logger().info('env_mod: "%s"' % msg.data)

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