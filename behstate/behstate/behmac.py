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
from yasmin import State
from yasmin import Blackboard
from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub


# define state Idle
class IdleState(State):
    def __init__(self) -> None:
        super().__init__(["driving_state"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state IDLE")
        # Simulate waiting for start trigger from adapt_vi
        while not blackboard.adapt_vi_start_trigger:
            time.sleep(0.1)
        return "driving_state"


# define state Driving
class DrivingState(State):
    def __init__(self) -> None:
        super().__init__(["drive", "stop_obstacle", "stop_near_park"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state DRIVING")
        time.sleep(3)

        # Dummy condition checks
        if blackboard.adapt_envmod:
            print("Obstacle detected by adapt_envmod")
            return "stop_obstacle"

        # Calculate distance to parking spot
        vehicle_location = blackboard.adapt_loc
        parking_spot_location = blackboard.adapt_roucomp
        distance_to_parking_spot = math.sqrt(
            (parking_spot_location[0] - vehicle_location[0]) ** 2 +
            (parking_spot_location[1] - vehicle_location[1]) ** 2
        )

        if distance_to_parking_spot < blackboard.parking_threshold:
            print("Near parking spot")
            return "stop_near_park"

        return "drive"


# define state StopObstacle
class StopObstacleState(State):
    def __init__(self) -> None:
        super().__init__(["idle"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state STOP_OBSTACLE")
        time.sleep(2)
        return "idle"


# define state StopNearPark
class StopNearParkState(State):
    def __init__(self) -> None:
        super().__init__(["park"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state STOP_NEAR_PARK")
        time.sleep(2)
        # Trigger parking procedure
        blackboard.adapt_trajp = True
        return "park"


# define state Park
class ParkState(State):
    def __init__(self) -> None:
        super().__init__(["idle"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state PARK")
        # Simulate parking process
        time.sleep(2)
        return "idle"


# main
def main():

    print("yasmin_demo")

    # init ROS 2
    rclpy.init()

    # create a FSM
    sm = StateMachine(outcomes=["finished"])

    # create and set blackboard
    blackboard = Blackboard()
    blackboard.obstacle_detected = False
    blackboard.near_parking_spot = False
    blackboard.adapt_vi_start_trigger = False  # Initial state of the start trigger
    blackboard.adapt_loc = (0, 0)  # Initialize adapt_loc with a tuple representing coordinates
    blackboard.adapt_obj = None  # Initialize adapt_obj
    blackboard.adapt_livtrac = None  # Initialize adapt_livtrac
    blackboard.adapt_roucomp = (10, 10)  # Initialize adapt_roucomp with a dummy parking spot location
    blackboard.adapt_trajp = False  # Initialize adapt_trajp
    blackboard.adapt_envmod = False  # Initialize adapt_envmod as no obstacle detected
    blackboard.parking_threshold = 1.0  # Distance threshold for parking spot detection

    # add states
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
        StopObstacleState(),
        transitions={
            "idle": "IDLE"
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
            "idle": "IDLE"
        }
    )

    # pub FSM info
    YasminViewerPub("YASMIN_DEMO", sm)

    # Set the start trigger to True after a delay to simulate an external trigger
    time.sleep(2)
    blackboard.adapt_vi_start_trigger = True

    # Simulate vehicle driving and detecting an obstacle and nearing parking spot
    time.sleep(5)
    blackboard.adapt_envmod = True  # Simulate obstacle detection

    # execute FSM
    outcome = sm.execute(blackboard)
    print(outcome)

    # shutdown ROS 2
    rclpy.shutdown()


if __name__ == "__main__":
    main()

