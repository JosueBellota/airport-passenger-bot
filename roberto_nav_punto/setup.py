from setuptools import find_packages
from setuptools import setup
import os
from glob import glob

package_name = 'roberto_nav_punto'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Josue',
    author_email='josue@example.com',
    description='Paquete de navegacion y seguimiento para Roberto',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'face_vision_node = roberto_nav_punto.face_vision_node:main',
            'vision_server = roberto_nav_punto.vision_server:main',
            'simple_follower = roberto_nav_punto.simple_follower:main',
            'person_tracker = roberto_nav_punto.person_tracker:main',
        ],
    },
)
