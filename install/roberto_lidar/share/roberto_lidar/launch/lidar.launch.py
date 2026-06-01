from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    lidar_node = Node(
        package='hls_lfcd_lds_driver',
        executable='hlds_laser_publisher',
        name='lidar_publisher',
        output='screen',
        parameters=[{
            'port': '/dev/ttyUSB0',
            'frame_id': 'base_scan',
            'baudrate': 230400
        }]
    )

    return LaunchDescription([
        lidar_node
    ])