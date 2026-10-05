from launch import LaunchDescription # type: ignore
from launch_ros.actions import Node

def generate_launch_description():
    launch_description = LaunchDescription()
    object_association_node = Node(
        package="boat_perception_fusion",
        executable="object_association_node",
        name="object_association",
        output="screen"
    )

    launch_description.add_action(object_association_node)
    return launch_description