#!/usr/bin/env python3

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from yasmin import State
from yasmin import Blackboard
from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub

import logging
import threading

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG)

class FSMNode(Node):
    def __init__(self, blackboard):
        super().__init__('fsm_node')
        self.blackboard = blackboard

        # Subscriptions
        self.create_subscription(Bool, '/vi_boolean', self.vi_start_callback, 10)
        self.create_subscription(Bool, '/route_state', self.route_state_callback, 10)
        self.create_subscription(Bool, '/reach_goal', self.reach_goal_callback, 10)
        self.create_subscription(Bool, '/stop', self.stop_callback, 10)
        self.create_subscription(Bool, '/final_state', self.final_state_callback, 10)

        # Publishers
        self.drive_publisher = self.create_publisher(Bool, '/drive', 10)
        self.park_publisher = self.create_publisher(Bool, '/park', 10)

        # Timer to publish /drive and /park every 0.01 seconds
        self.timer = self.create_timer(0.01, self.timer_callback)

        logging.debug("Initialized FSM Node")

    def vi_start_callback(self, msg):
        if msg.data:
            logging.info("Received vi_start with True")
            self.blackboard.adapt_vi_start_trigger = True
            # Publish to /drive topic when /vi_boolean is True
            drive_msg = Bool()
            drive_msg.data = True
            self.drive_publisher.publish(drive_msg)
        else:
            self.blackboard.adapt_vi_start_trigger = False
        logging.debug(f"Received vi_start callback: {msg.data}")

    def route_state_callback(self, msg):
        self.blackboard.adapt_roucomp = msg.data
        logging.debug(f"Received route_state callback: {msg.data}")

        if msg.data:
            drive_msg = Bool()
            drive_msg.data = True
            self.drive_publisher.publish(drive_msg)
            logging.info("Route computed, published to /drive topic")

    def stop_callback(self, msg):
        self.blackboard.adapt_envmod = msg.data
        logging.debug(f"Received stop callback: {msg.data}")

        # Check if an obstacle is detected or removed
        if msg.data:
            logging.info("Obstacle detected by adapt_envmod")
            # Publish to /drive topic with False
            drive_msg = Bool()
            drive_msg.data = False
            self.drive_publisher.publish(drive_msg)
        else:
            logging.info("Obstacle removed by adapt_envmod")

        # Check if in ParkingState and /stop is False
        if not msg.data and self.blackboard.current_state == "parking":
            self.blackboard.stop_removed_during_parking = True

    def reach_goal_callback(self, msg):
        self.blackboard.reach_goal = msg.data
        logging.debug(f"Received reach_goal callback: {msg.data}")

    def final_state_callback(self, msg):
        self.blackboard.final_state = msg.data
        logging.debug(f"Received final_state callback: {msg.data}")

    def timer_callback(self):
        drive_msg = Bool()
        drive_msg.data = self.blackboard.adapt_vi_start_trigger and not self.blackboard.adapt_envmod
        self.drive_publisher.publish(drive_msg)

        park_msg = Bool()
        park_msg.data = self.blackboard.adapt_trajp
        self.park_publisher.publish(park_msg)

class IdleState(State):
    def __init__(self) -> None:
        super().__init__(["drive_state"])
        self.logger = logging.getLogger('IdleState')

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state IDLE")
        # Wait for start trigger from adapt_vi
        while not blackboard.adapt_vi_start_trigger:
            self.logger.info('Waiting for start trigger from adapt_vi')
            time.sleep(0.1)
        return "drive_state"

class DriveState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["drive", "stop_when_obstacle_detected", "stop_near_parking_spot"])
        self.fsm_node = fsm_node

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state DRIVE")
        time.sleep(3)  # Simulate driving

        # Check if the goal has been reached
        if blackboard.reach_goal:  # Check the reach_goal flag on the blackboard
            logging.info("Goal reached, transitioning to stop_near_parking_spot")
            return "stop_near_parking_spot"

        # Check for obstacle detection
        if blackboard.adapt_envmod:
            logging.info("Obstacle detected by adapt_envmod")
            blackboard.previous_state = "drive"
            return "stop_when_obstacle_detected"

        # Keep driving otherwise
        return "drive"

class StopWhenObstacleDetectedState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["stop", "drive", "parking"])
        self.fsm_node = fsm_node

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state STOP_WHEN_OBSTACLE_DETECTED")

        # Publish to /drive topic with False when obstacle is detected
        drive_msg = Bool()
        drive_msg.data = False
        self.fsm_node.drive_publisher.publish(drive_msg)
        logging.info("Published to /drive topic with False")

        # Wait for the obstacle to be removed
        while blackboard.adapt_envmod:
            time.sleep(0.1)

        logging.info("Obstacle removed, returning to previous state")
        return blackboard.previous_state

class StopNearParkingSpotState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["parking"])
        self.fsm_node = fsm_node

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state STOP_NEAR_PARKING_SPOT")
        time.sleep(2)
        # Trigger parking procedure
        blackboard.adapt_trajp = True
        # Publish to /park topic
        park_msg = Bool()
        park_msg.data = True
        self.fsm_node.park_publisher.publish(park_msg)
        return "parking"

class ParkingState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["parked", "stop_when_obstacle_detected", "parking"])
        self.fsm_node = fsm_node

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state PARKING")

        blackboard.current_state = "parking"

        while not blackboard.final_state:
            time.sleep(0.1)
            # Check if obstacle detected during parking
            if blackboard.adapt_envmod:
                logging.info("Obstacle detected during parking")
                blackboard.previous_state = "parking"
                return "stop_when_obstacle_detected"
            # Check if obstacle removed during parking
            if blackboard.stop_removed_during_parking:
                blackboard.stop_removed_during_parking = False
                return "parking"

        return "parked"

class ParkedState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["idle"])
        self.fsm_node = fsm_node

    def execute(blackboard: Blackboard) -> str:
        logging.debug("Executing state PARKED")
        return "finished"

def main():
    logging.info("Starting yasmin_demo")

    try:
        # Initialize ROS 2
        rclpy.init()

        # Create a StateMachine
        sm = StateMachine(outcomes=["finished"])

        # Create and set blackboard
        blackboard = Blackboard()
        blackboard.adapt_vi_start_trigger = False  # Initial state of the start trigger
        blackboard.adapt_roucomp = False  # Initialize adapt_roucomp to indicate route not computed
        blackboard.adapt_trajp = False  # Initialize adapt_trajp
        blackboard.adapt_envmod = False  # Initialize adapt_envmod as no obstacle detected
        blackboard.reach_goal = False  # Initialize reach_goal
        blackboard.final_state = False  # Initialize final_state
        blackboard.previous_state = "idle"  # Initialize previous_state
        blackboard.current_state = "idle"  # Track current state
        blackboard.stop_removed_during_parking = False  # Track if obstacle removed during parking

        # Initialize ROS 2 node and publishers
        fsm_node = FSMNode(blackboard)

        # Add states to the StateMachine
        sm.add_state(
            "IDLE",
            IdleState(),
            transitions={"drive_state": "DRIVE"}
        )
        sm.add_state(
            "DRIVE",
            DriveState(fsm_node),
            transitions={
                "drive": "DRIVE",
                "stop_when_obstacle_detected": "STOP_WHEN_OBSTACLE_DETECTED",
                "stop_near_parking_spot": "STOP_NEAR_PARKING_SPOT"
            }
        )
        sm.add_state(
            "STOP_WHEN_OBSTACLE_DETECTED",
            StopWhenObstacleDetectedState(fsm_node),
            transitions={
                "stop": "finished",
                "drive": "DRIVE",
                "parking": "PARKING"
            }
        )
        sm.add_state(
            "STOP_NEAR_PARKING_SPOT",
            StopNearParkingSpotState(fsm_node),
            transitions={"parking": "PARKING"}
        )
        sm.add_state(
            "PARKING",
            ParkingState(fsm_node),
            transitions={
                "parked": "PARKED",
                "stop_when_obstacle_detected": "STOP_WHEN_OBSTACLE_DETECTED",
                "parking": "PARKING"
            }
        )
        sm.add_state(
            "PARKED",
            ParkedState(fsm_node),
            transitions={"idle": "finished"}
        )

        # Initialize Yasmin viewer
        YasminViewerPub("YASMIN_DEMO", sm)

        # Execute FSM in a separate thread
        def execute_fsm():
            try:
                outcome = sm.execute(blackboard)
                logging.info(f"FSM execution outcome: {outcome}")
            except Exception as e:
                logging.error(f"FSM execution error: {e}")

        fsm_thread = threading.Thread(target=execute_fsm)
        fsm_thread.start()

        # Spin ROS 2 node
        rclpy.spin(fsm_node)

        # Cleanup on shutdown
        fsm_thread.join()
        fsm_node.destroy_node()
        rclpy.shutdown()

    except KeyboardInterrupt:
        logging.info("yasmin_demo interrupted by user")
        rclpy.shutdown()

if __name__ == "__main__":
    main()
