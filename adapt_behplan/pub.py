import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class BehplanPub(Node):

    def __init__(self):
        super().__init__('beh_plan')
        self.publisher_ = self.create_publisher(String, 'beh_speed/speed', 10)
        self.publisher_ = self.create_publisher(String, 'beh_wp/wp', 10)
        self.publisher_ = self.create_publisher(String, 'beh_mc/mc', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

       

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello Team: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    behplan = BehplanPub()

    rclpy.spin(behplan)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    behplan.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()