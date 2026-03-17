from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[
        ],
    )

    controller_node = Node(
        package='minibot_xbox_joy',
        executable='controller_node',
        name='controller_node',
        output='screen',
        parameters=[
            {'in_topic': '/joy'},
            {'out_topic': '/edu_sml/joy'},
        ],
    )

    return LaunchDescription([
        joy_node,
        controller_node,
    ])