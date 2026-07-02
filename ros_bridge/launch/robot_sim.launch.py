from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
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
    initial_battery_arg = DeclareLaunchArgument(
        "initial_battery",
        default_value="100.0",
        description="Initial battery level",
    )

    robot_node = Node(
        package="ros_bridge",
        executable="robot_node",
        name="robot_simulator",
        output="screen",
        parameters=[
            {
                "robot_id": LaunchConfiguration("robot_id"),
                "initial_x": LaunchConfiguration("initial_x"),
                "initial_y": LaunchConfiguration("initial_y"),
                "initial_battery": LaunchConfiguration("initial_battery"),
                "status": "Moving",
            }
        ],
    )

    return LaunchDescription(
        [
            robot_id_arg,
            initial_x_arg,
            initial_y_arg,
            initial_battery_arg,
            robot_node,
        ]
    )
