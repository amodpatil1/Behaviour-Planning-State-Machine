from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='adapt_behplan',
            namespace='behaviour',
            executable='behaviour_node',
            name='behplan'
        )
    ])