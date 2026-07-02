from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_dir = get_package_share_directory("ros_bridge")

    robot_id_arg = DeclareLaunchArgument(
        "robot_id",
        default_value="1",
        description="Robot ID for MQTT topic routing",
    )
    initial_x_arg = DeclareLaunchArgument(
        "initial_x",
        default_value="0.0",
        description="Initial X position",
    )
    initial_y_arg = DeclareLaunchArgument(
        "initial_y",
        default_value="0.0",
        description="Initial Y position",
    )
    mqtt_broker_arg = DeclareLaunchArgument(
        "mqtt_broker",
        default_value="localhost",
        description="MQTT broker address",
    )

    robot_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, "launch", "robot_sim.launch.py")
        ),
        launch_arguments={
            "robot_id": LaunchConfiguration("robot_id"),
            "initial_x": LaunchConfiguration("initial_x"),
            "initial_y": LaunchConfiguration("initial_y"),
        }.items(),
    )

    mqtt_bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, "launch", "mqtt_bridge.launch.py")
        ),
        launch_arguments={
            "robot_id": LaunchConfiguration("robot_id"),
            "mqtt_broker": LaunchConfiguration("mqtt_broker"),
        }.items(),
    )

    return LaunchDescription(
        [
            robot_id_arg,
            initial_x_arg,
            initial_y_arg,
            mqtt_broker_arg,
            robot_sim_launch,
            mqtt_bridge_launch,
        ]
    )
