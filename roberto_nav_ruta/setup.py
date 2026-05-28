from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'roberto_nav_ruta'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'map'), glob('map/*.pgm') + glob('map/*.yaml')),
        (os.path.join('share', package_name, 'param'), glob('param/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mmalgbon',
    maintainer_email='mmalgbon@todo.todo',
    description='Navegación por rutas para Roberto',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'follow_waypoints = roberto_nav_ruta.follow_waypoints:main',
            'navigate_to_pose = roberto_nav_ruta.navigate_to_pose:main',
            'test_navigation = roberto_nav_ruta.test_navigation:main',
        ],
    },
)