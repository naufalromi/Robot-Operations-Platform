from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ros_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robot Ops Team',
    maintainer_email='dev@robotops.io',
    description='ROS2 bridge for Robot Operations Platform',
    license='MIT',
    entry_points={
        'console_scripts': [
            'robot_node = ros_bridge.robot_node:main',
            'mqtt_bridge = ros_bridge.mqtt_bridge:main',
        ],
    },
)
