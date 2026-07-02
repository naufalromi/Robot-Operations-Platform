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
    mqtt_broker_arg = DeclareLaunchArgument(
        "mqtt_broker",
        default_value="localhost",
        description="MQTT broker address",
    )
    mqtt_port_arg = DeclareLaunchArgument(
        "mqtt_port",
        default_value="1883",
        description="MQTT broker port",
    )

    bridge_node = Node(
        package="ros_bridge",
        executable="mqtt_bridge",
        name="mqtt_bridge",
        output="screen",
        parameters=[
            {
                "robot_id": LaunchConfiguration("robot_id"),
                "mqtt_broker": LaunchConfiguration("mqtt_broker"),
                "mqtt_port": LaunchConfiguration("mqtt_port"),
            }
        ],
    )

    return LaunchDescription(
        [
            robot_id_arg,
            mqtt_broker_arg,
            mqtt_port_arg,
            bridge_node,
        ]
    )
