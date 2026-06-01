from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='roberto_gesture_detection',
            executable='gesture_detector',
            name='gesture_detector',
            output='screen',
            emulate_tty=True,
        ),
    ])