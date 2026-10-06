"""Start Nav2 and the cmd_vel bridge for the boat.

Velocity path (names matter, a missed remap means the boat silently does not move):

    controller_server --cmd_vel_nav--> velocity_smoother --cmd_vel--> cmd_vel_bridge

Odometry and TF (/odometry/filtered and map -> odom -> base_link) are NOT started
here. They come from perception's estimator, or the sim stand-in until it exists.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('boat_bringup'), 'config', 'nav2_params.yaml')

    # Nav2 servers. Each name here must match the top-level key in nav2_params.yaml.
    nav2_nodes = [
        ('nav2_controller', 'controller_server', [('cmd_vel', 'cmd_vel_nav')]),
        ('nav2_smoother', 'smoother_server', []),
        ('nav2_planner', 'planner_server', []),
        ('nav2_behaviors', 'behavior_server', [('cmd_vel', 'cmd_vel_nav')]),
        ('nav2_bt_navigator', 'bt_navigator', []),
        ('nav2_velocity_smoother', 'velocity_smoother',
         [('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', 'cmd_vel')]),
    ]

    actions = []
    for package, executable, remappings in nav2_nodes:
        actions.append(Node(
            package=package,
            executable=executable,
            name=executable,
            output='screen',
            parameters=[params_file],
            remappings=remappings,
        ))

    # Brings the servers above up in order (configure, then activate).
    actions.append(Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [name for _, name, _ in nav2_nodes],
        }],
    ))

    # Turns /cmd_vel into MAVROS setpoints and holds the 0.5 s watchdog.
    # Runs on wall time: its timer is a wall timer, so the age check uses the same clock.
    actions.append(Node(
        package='boat_nav',
        executable='cmd_vel_bridge',
        name='cmd_vel_bridge',
        output='screen',
        parameters=[{'use_sim_time': False}],
    ))

    return LaunchDescription(actions)
