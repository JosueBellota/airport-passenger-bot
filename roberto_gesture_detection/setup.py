from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'roberto_gesture_detection'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Incluir archivos launch
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Incluir archivos de configuración si los tienes
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mmalgbon',
    maintainer_email='mmalgbon@todo.todo',
    description='Gesture detection for TurtleBot3 - Call robot with thumb',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gesture_detector = roberto_gesture_detection.gesture_detector:main',
            
        ],
    },
)