#!/usr/bin/env python3

# Copyright (C) 2023  Miguel Ángel González Santamarta

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Pose
from yasmin import State
from yasmin import Blackboard
from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub

# Import logging module
import logging

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG)

class FSMNode(Node):
    def __init__(self, blackboard):
        super().__init__('fsm_node')
        self.blackboard = blackboard

        # Subscriptions
        self.create_subscription(Bool, '/vi_start', self.vi_start_callback, 10)
        self.create_subscription(Pose, '/loc_pose', self.loc_pose_callback, 10)
        self.create_subscription(Bool, '/stop', self.stop_callback, 10)
        self.create_subscription(Pose, '/route', self.route_callback, 10)
        self.create_subscription(Bool, '/trajpf', self.trajpf_callback, 10)
        self.create_subscription(Bool, '/trajpr', self.trajpr_callback, 10)

        # Publisher for /stop_obs topic
        self.adapt_trajp_obs_publisher = self.create_publisher(Bool, '/stop_obs', 10)

        logging.debug("Initialized FSM Node")

    def vi_start_callback(self, msg):
        self.blackboard.adapt_vi_start_trigger = msg.data
        logging.debug(f"Received vi_start callback: {msg.data}")

    def loc_pose_callback(self, msg):
        self.blackboard.adapt_loc = (msg.position.x, msg.position.y)
        logging.debug(f"Received loc_pose callback: x={msg.position.x}, y={msg.position.y}")

    def stop_callback(self, msg):
        self.blackboard.adapt_envmod = msg.data
        logging.debug(f"Received stop callback: {msg.data}")

        # Inform adapt_trajp to stop if obstacle detected
        if msg.data:  # Assuming True means obstacle detected
            logging.info("Obstacle detected by adapt_envmod")
            # Publish to /stop_obs topic
            stop_obs_msg = Bool()
            stop_obs_msg.data = True
            self.adapt_trajp_obs_publisher.publish(stop_obs_msg)

    def route_callback(self, msg):
        self.blackboard.adapt_roucomp = (msg.position.x, msg.position.y)
        logging.debug(f"Received route callback: x={msg.position.x}, y={msg.position.y}")

    def trajpf_callback(self, msg):
        self.blackboard.trajpf_complete = msg.data
        logging.debug(f"Received trajpf callback: {msg.data}")

    def trajpr_callback(self, msg):
        self.blackboard.trajpr_complete = msg.data
        logging.debug(f"Received trajpr callback: {msg.data}")


# Define state Idle
class IdleState(State):
    def __init__(self) -> None:
        super().__init__(["driving_state"])
        self.logger = logging.getLogger('IdleState')

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state IDLE")
        # Wait for start trigger from adapt_vi
        while not blackboard.adapt_vi_start_trigger:
            self.logger.info('Waiting for start trigger from adapt_vi')
            time.sleep(0.1)
        return "driving_state"


# Define state Driving
class DrivingState(State):
    def __init__(self) -> None:
        super().__init__(["drive", "stop_obstacle", "stop_near_park"])

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state DRIVING")
        time.sleep(3)

        # Check for obstacle detection
        if blackboard.adapt_envmod:
            logging.info("Obstacle detected by adapt_envmod")
            return "stop_obstacle"

        # Calculate distance to parking spot
        vehicle_location = blackboard.adapt_loc
        parking_spot_location = blackboard.adapt_roucomp
        distance_to_parking_spot = math.sqrt(
            (parking_spot_location[0] - vehicle_location[0]) ** 2 +
            (parking_spot_location[1] - vehicle_location[1]) ** 2
        )

        if distance_to_parking_spot < blackboard.parking_threshold:
            logging.debug("Near parking spot")
            blackboard.adapt_trajp = True
            return "stop_near_park"

        return "drive"


# Define state StopObstacle
class StopObstacleState(State):
    def __init__(self, fsm_node) -> None:
        super().__init__(["stop"])
        self.fsm_node = fsm_node

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state STOP_OBSTACLE")
        time.sleep(2)

        # Check if adapt_envmod detects an obstacle (assuming adapt_envmod is True means obstacle detected)
        if blackboard.adapt_envmod:
            logging.info("Obstacle detected by adapt_envmod")
            # Publish to /stop_obs topic using FSMNode's publisher
            stop_obs_msg = Bool()
            stop_obs_msg.data = True
            self.fsm_node.adapt_trajp_obs_publisher.publish(stop_obs_msg)

        return "stop"


# Define state StopNearPark
class StopNearParkState(State):
    def __init__(self) -> None:
        super().__init__(["park"])

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state STOP_NEAR_PARK")
        time.sleep(2)
        # Trigger parking procedure
        blackboard.adapt_trajp = True
        return "park"


# Define state Park
class ParkState(State):
    def __init__(self) -> None:
        super().__init__(["parked"])

    def execute(self, blackboard: Blackboard) -> str:
        logging.debug("Executing state PARK")

        while not blackboard.trajpf_complete:
            time.sleep(0.1)

        while not blackboard.trajpr_complete:
            time.sleep(0.1)

        logging.info("Vehicle parked")
        return "parked"


# Main function
def main():
    logging.info("Starting yasmin_demo")

    # Initialize ROS 2
    rclpy.init()

    # Create a StateMachine
    sm = StateMachine(outcomes=["finished"])

    # Create and set blackboard
    blackboard = Blackboard()
    blackboard.adapt_vi_start_trigger = False  # Initial state of the start trigger
    blackboard.adapt_loc = (0, 0)  # Initialize adapt_loc with a tuple representing coordinates
    blackboard.adapt_roucomp = (10, 10)  # Initialize adapt_roucomp with a dummy parking spot location
    blackboard.adapt_trajp = False  # Initialize adapt_trajp
    blackboard.adapt_envmod = False  # Initialize adapt_envmod as no obstacle detected
    blackboard.parking_threshold = 1.0  # Distance threshold for parking spot detection
    blackboard.trajpf_complete = False  # Initialize trajpf_complete
    blackboard.trajpr_complete = False  # Initialize trajpr_complete

    # Initialize ROS 2 node and publishers
    fsm_node = FSMNode(blackboard)

    # Add states to the StateMachine
    sm.add_state(
        "IDLE",
        IdleState(),
        transitions={
            "driving_state": "DRIVING"
        }
    )
    sm.add_state(
        "DRIVING",
        DrivingState(),
        transitions={
            "drive": "DRIVING",
            "stop_obstacle": "STOP_OBSTACLE",
            "stop_near_park": "STOP_NEAR_PARK"
        }
    )
    sm.add_state(
        "STOP_OBSTACLE",
        StopObstacleState(fsm_node),
        transitions={
            "stop": "STOP_OBSTACLE"
        }
    )
    sm.add_state(
        "STOP_NEAR_PARK",
        StopNearParkState(),
        transitions={
            "park": "PARK"
        }
    )
    sm.add_state(
        "PARK",
        ParkState(),
        transitions={
            "parked": "PARKED"
        }
    )

    # Initialize Yasmin viewer
    YasminViewerPub("YASMIN_DEMO", sm)

    # Execute FSM in a separate thread
    import threading

    def execute_fsm():
        outcome = sm.execute(blackboard)
        logging.info(f"FSM execution outcome: {outcome}")

    fsm_thread = threading.Thread(target=execute_fsm)
    fsm_thread.start()

    # Spin ROS 2 node
    rclpy.spin(fsm_node)

    # Shutdown
    fsm_thread.join()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
