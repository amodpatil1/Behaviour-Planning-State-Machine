import unittest
from unittest.mock import MagicMock
from std_msgs.msg import Bool
import rclpy
from rclpy.node import Node
import time  # Ensure the time module is imported

# Adjust the import to match your file name
from beh import FSMNode, Blackboard, IdleState, DriveState, StopWhenObstacleDetectedState, StopNearParkingSpotState, ParkedState

class TestFSMNode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('test_fsm_node')
        cls.blackboard = Blackboard()
        cls.fsm_node = FSMNode(cls.blackboard)
        
        cls.drive_received = None
        cls.park_received = None

        cls.drive_subscriber = cls.node.create_subscription(Bool, '/drive', cls.drive_callback, 10)
        cls.park_subscriber = cls.node.create_subscription(Bool, '/park', cls.park_callback, 10)
        
        cls.drive_publisher = cls.node.create_publisher(Bool, '/drive', 10)
        cls.park_publisher = cls.node.create_publisher(Bool, '/park', 10)
        
        time.sleep(1)  # Allow time for publishers/subscribers to be set up

    @classmethod
    def tearDownClass(cls):
        cls.fsm_node.destroy_node()
        cls.node.destroy_node()
        rclpy.shutdown()

    @classmethod
    def drive_callback(cls, msg):
        cls.drive_received = msg.data

    @classmethod
    def park_callback(cls, msg):
        cls.park_received = msg.data

    def test_idle_to_drive_transition(self):
        self.blackboard.route_state = True
        idle_state = IdleState(self.blackboard, self.node)
        idle_state.on_enter()
        new_state = idle_state.update()

        self.assertIsInstance(new_state, DriveState)
        self.assertTrue(self.drive_received, "FSM did not transition to DriveState correctly")

    def test_drive_to_stop_when_obstacle_detected_transition(self):
        self.blackboard.stop = True
        drive_state = DriveState(self.blackboard, self.node)
        drive_state.on_enter()
        new_state = drive_state.update()

        self.assertIsInstance(new_state, StopWhenObstacleDetectedState)
        self.assertFalse(self.drive_received, "FSM did not transition to StopWhenObstacleDetectedState correctly")

    def test_stop_when_obstacle_detected_to_drive_transition(self):
        self.blackboard.stop = False
        stop_state = StopWhenObstacleDetectedState(self.blackboard, self.node)
        stop_state.on_enter()
        new_state = stop_state.update()

        self.assertIsInstance(new_state, DriveState)
        self.assertTrue(self.drive_received, "FSM did not transition back to DriveState correctly")

    def test_stop_near_parking_spot_transition(self):
        self.blackboard.final_state = True
        stop_near_park_state = StopNearParkingSpotState(self.blackboard, self.node)
        stop_near_park_state.on_enter()
        new_state = stop_near_park_state.update()

        self.assertIsInstance(new_state, ParkedState)
        self.assertTrue(self.park_received, "FSM did not transition to ParkedState correctly")

if __name__ == '__main__':
    unittest.main()



