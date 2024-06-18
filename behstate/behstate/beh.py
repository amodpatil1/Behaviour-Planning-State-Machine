import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32, Bool
from geometry_msgs.msg import Point  # Assuming location data uses geometry_msgs/Point

class BehaviorPlanningNode(Node):
    def __init__(self):
        super().__init__('behavior_planning_node')
        
        # Subscribers
        self.subscription1 = self.create_subscription(
            Bool,
            '/vi_start',  # adapt_vi topic
            self.start_trigger_callback,
            10
        )
        self.subscription2 = self.create_subscription(
            Int32,
            '/obstacle_distance',  # Example placeholder for adapt_env_mod
            self.obstacle_distance_callback,
            10
        )
        self.subscription3 = self.create_subscription(
            Bool,
            '/stop',  # adapt_env_mod topic
            self.adapt_envmod_callback,
            10
        )
        self.subscription4 = self.create_subscription(
            Point,
            '/loc_pose',  # adapt_loc topic
            self.adapt_loc_callback,
            10
        )
        self.subscription5 = self.create_subscription(
            String,
            '/live_loc',  # adapt_livtrac topic
            self.adapt_livtrac_callback,
            10
        )
        self.subscription6 = self.create_subscription(
            Point,
            '/route',  # adapt_roucomp topic
            self.adapt_roucomp_callback,
            10
        )
        self.subscription7 = self.create_subscription(
            String,
            '/traj',  # adapt_trajp topic
            self.adapt_trajp_callback,
            10
        )
        
        # Publisher for adapt_trajp (assuming it may also publish for testing)
        self.trajp_publisher = self.create_publisher(String, '/traj', 10)
        
        # Variables to store topic data
        self.start_trigger = False
        self.obstacle_distance = None
        self.parking_spot_detected = False
        self.adapt_loc_data = None
        self.adapt_obj_data = None
        self.adapt_livtrac_data = None
        self.adapt_roucomp_data = None
        self.adapt_trajp_data = None
        self.adapt_envmod_data = False
        
        # States
        self.state = 'IDLE'
        
        # Timer to regularly invoke the behavior planning logic
        self.timer = self.create_timer(1.0, self.behavior_planning_callback)
    
    def start_trigger_callback(self, msg):
        self.start_trigger = msg.data
        self.get_logger().info(f"Received start trigger from adapt_vi: {self.start_trigger}")
    
    def obstacle_distance_callback(self, msg):
        self.obstacle_distance = msg.data
        self.get_logger().info(f"Received obstacle distance: {self.obstacle_distance}")
    
    def adapt_envmod_callback(self, msg):
        self.adapt_envmod_data = msg.data
        self.get_logger().info(f"Received adapt_envmod data: {self.adapt_envmod_data}")
    
    def adapt_loc_callback(self, msg):
        self.adapt_loc_data = msg
        self.get_logger().info(f"Received adapt_loc data: {self.adapt_loc_data}")
    
    def adapt_livtrac_callback(self, msg):
        self.adapt_livtrac_data = msg.data
        self.get_logger().info(f"Received adapt_livtrac data: {self.adapt_livtrac_data}")
    
    def adapt_roucomp_callback(self, msg):
        self.adapt_roucomp_data = msg
        self.get_logger().info(f"Received adapt_roucomp data: {self.adapt_roucomp_data}")
        # Check if adapt_roucomp_data indicates start of route or drive condition
        if self.state == 'DRIVING' and self.adapt_roucomp_data == "start_route":
            self.get_logger().info("Action: Drive")
            # Additional logic specific to starting the drive outcome
        
    def adapt_trajp_callback(self, msg):
        self.adapt_trajp_data = msg.data
        self.get_logger().info(f"Received adapt_trajp data: {self.adapt_trajp_data}")
    
    def behavior_planning_callback(self):
        if self.state == 'IDLE':
            self.idle_state()
        elif self.state == 'DRIVING':
            self.driving_state()
        elif self.state == 'PARK':
            self.park_state()
    
    def idle_state(self):
        if self.start_trigger:
            self.state = 'DRIVING'
            self.get_logger().info("Transitioning to DRIVING state")
    
    def driving_state(self):
        if self.adapt_envmod_data:
            self.get_logger().info("Action: Stop due to detected object")
            self.state = 'IDLE'
        elif self.parking_spot_detected and self.adapt_roucomp_data and self.adapt_loc_data:
            distance = self.calculate_distance(self.adapt_loc_data, self.adapt_roucomp_data)
            if distance < 1.0:  # Assuming 1.0 is the threshold distance
                self.get_logger().info("Action: Stop near parking spot")
                self.state = 'PARK'
                self.initiate_parking()
        else:
            self.get_logger().info("Waiting for adapt_roucomp to initiate drive...")
            # Additional logic specific to waiting for adapt_roucomp to initiate drive
    
    def park_state(self):
        self.get_logger().info("In PARK state")
        # Add parking logic here
    
    def initiate_parking(self):
        park_command = String()
        park_command.data = "Park"
        self.trajp_publisher.publish(park_command)
        self.get_logger().info("Sent parking command to adapt_trajp")
    
    def calculate_distance(self, loc1, loc2):
        dx = loc1.x - loc2.x
        dy = loc1.y - loc2.y
        dz = loc1.z - loc2.z
        return (dx**2 + dy**2 + dz**2)**0.5
    
def main(args=None):
    rclpy.init(args=args)
    node = BehaviorPlanningNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

