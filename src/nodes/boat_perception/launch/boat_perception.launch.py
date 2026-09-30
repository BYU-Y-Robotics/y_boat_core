from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='boat_perception',
            executable='lidar_processor',
            name='lidar_processor',
            output='screen',
        ),
    ])
