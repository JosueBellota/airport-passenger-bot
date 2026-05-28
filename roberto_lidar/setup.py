from setuptools import setup

package_name = 'roberto_lidar'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/lidar.launch.py']),
        ('share/' + package_name + '/rviz', ['rviz/rviz_lidar_config.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cyorpul',
    description='LiDAR obstacle detection package',

    entry_points={
        'console_scripts': [
      		 'obstacle_detection_node = roberto_lidar.obstacle_detection_node:main',
             'obstacle_avoidance = roberto_lidar.obstacle_avoidance_node:main',
        ],
    },
)
