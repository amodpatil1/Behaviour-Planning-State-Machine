import rclpy
from yasmin_ros.yasmin_node import YasminNode
import time
from yasmin import State, Blackboard, StateMachine
from yasmin_viewer import YasminViewerPub
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from sensor_msgs.msg import LaserScan

class IdleState(State):
    def __init__(self):
        super().__init__(["driving_state"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state IDLE")
        while not blackboard.adapt_vi_start_trigger:
            time.sleep(0.1)
        return "driving_state"


class DrivingState(State):
    def __init__(self):
        super().__init__(["drive", "stop_obstacle", "stop_near_park"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state DRIVING")
        if blackboard.adapt_roucomp:
            if blackboard.obstacle_detected:
                return "stop_obstacle"
            distance_to_parking = ((blackboard.adapt_loc[0] - blackboard.parking_spot_location[0]) ** 2 +
                                   (blackboard.adapt_loc[1] - blackboard.parking_spot_location[1]) ** 2) ** 0.5
            if distance_to_parking < blackboard.parking_threshold:
                return "stop_near_park"
            return "drive"
        return "drive"


class StopObstacleState(State):
    def __init__(self):
        super().__init__(["idle"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state STOP_OBSTACLE")
        time.sleep(2)
        return "idle"


class StopNearParkState(State):
    def __init__(self):
        super().__init__(["park"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state STOP_NEAR_PARK")
        time.sleep(2)
        return "park"


class ParkState(State):
    def __init__(self):
        super().__init__(["idle"])

    def execute(self, blackboard: Blackboard) -> str:
        print("Executing state PARK")
        time.sleep(2)
        return "idle"


class StateMachineSetup:
    def __init__(self, node):
        self.sm = StateMachine(outcomes=["finished"])

        self.blackboard = Blackboard()
        self.blackboard.obstacle_detected = False
        self.blackboard.adapt_vi_start_trigger = False
        self.blackboard.adapt_loc = (0, 0)
        self.blackboard.adapt_roucomp = False
        self.blackboard.parking_spot_location = (0, 0)
        self.blackboard.parking_threshold = 0.5

        self.sm.add_state("IDLE", IdleState(), transitions={"driving_state": "DRIVING"})
        self.sm.add_state("DRIVING", DrivingState(), transitions={"drive": "DRIVING", "stop_obstacle": "STOP_OBSTACLE", "stop_near_park": "STOP_NEAR_PARK"})
        self.sm.add_state("STOP_OBSTACLE", StopObstacleState(), transitions={"idle": "IDLE"})
        self.sm.add_state("STOP_NEAR_PARK", StopNearParkState(), transitions={"park": "PARK"})
        self.sm.add_state("PARK", ParkState(), transitions={"idle": "IDLE"})

        YasminViewerPub("YASMIN_DEMO", self.sm)

        node.create_subscription(String, '/vi_start', self.vi_start_callback, 10)
        node.create_subscription(Pose, '/loc_pose', self.loc_pose_callback, 10)
        node.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        node.create_subscription(Pose, '/route', self.route_callback, 10)

    def vi_start_callback(self, msg: String) -> None:
        self.blackboard.adapt_vi_start_trigger = "Start" in msg.data

    def loc_pose_callback(self, msg: Pose) -> None:
        self.blackboard.adapt_loc = (msg.position.x, msg.position.y)

    def scan_callback(self, msg: LaserScan) -> None:
        self.blackboard.obstacle_detected = any(r < 1.0 for r in msg.ranges if r > 0)

    def route_callback(self, msg: Pose) -> None:
        self.blackboard.adapt_roucomp = True
        self.blackboard.parking_spot_location = (msg.position.x, msg.position.y)

def main(args=None):
    rclpy.init(args=args)
    node = YasminNode.get_instance()
    StateMachineSetup(node)  # Initialize state machine setup
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

