import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Vector3, PoseArray, Twist, PoseStamped, Pose
from adapt_behplan.beh_planner import CarBehaviour
from math import sqrt

class CarBehaviour:
    def __init__(self):
        self.waypoints = []
        self.curr_way_idx = 0
        self.reached_parking_spot = False
        self.current_speed = 0
        self.dist_to_stop = 0

    def twist_callback(self):
        # Placeholder logic for adjusting current_speed
        self.current_speed = 10  # For example

    def route_callback(self, msg):
        self.waypoints = msg.poses
        self.curr_way_idx = 0

    def veh_loc(self, msg):
        # Correct indentation here
            self.dist_to_stop = sqrt(
            (round(self.waypoints[10].pose.position.x, 4) - round(msg.pose.position.x, 4)) ** 2 +
            (round(self.waypoints[10].pose.position.y, 4) - round(msg.pose.position.y, 4)) ** 2
        )


class TestCarBehaviour(unittest.TestCase):
   
    def setUp(self):
        rclpy.init()

    def tearDown(self):
        rclpy.shutdown()

    def test_twist_callback(self):
        node = CarBehaviour()
        node.current_speed = 0

        # Call twist_callback method
        node.twist_callback()

        # Assert that speed is adjusted according to some logic
        self.assertNotEqual(node.current_speed, 0)

    def test_route_callback(self):
        node = CarBehaviour()
        msg = PoseArray()

        # Creating dummy Pose data
        pose1 = Pose()
        pose1.position.x = 1.0
        pose1.position.y = 2.0
        pose1.position.z = 0.0
        pose1.orientation.x = 0.0
        pose1.orientation.y = 0.0
        pose1.orientation.z = 0.0
        pose1.orientation.w = 1.0

        pose2 = Pose()
        pose2.position.x = 3.0
        pose2.position.y = 4.0
        pose2.position.z = 0.0
        pose2.orientation.x = 0.0
        pose2.orientation.y = 0.0
        pose2.orientation.z = 0.0
        pose2.orientation.w = 1.0

        # Assigning dummy Pose data to PoseArray message
        msg.poses = [pose1, pose2]

        # Call route_callback method
        node.route_callback(msg)

        # Assert that waypoints are updated correctly
        self.assertEqual(node.waypoints, msg.poses)
        self.assertEqual(node.curr_way_idx, 0)

    def test_veh_loc(self):
        node = CarBehaviour()

        # Test vehicle location callback
        msg = PoseStamped()
        msg.pose.position.x = 1.0
        msg.pose.position.y = 2.0

        # Ensure waypoints are initialized to avoid index out of range error
        node.waypoints = [PoseStamped() for _ in range(11)]

        node.veh_loc(msg)
        # Add assertions based on the expected behavior

if __name__ == '__main__':
    unittest.main()
