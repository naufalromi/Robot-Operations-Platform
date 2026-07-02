import pytest
import rclpy
from std_msgs.msg import Float32, String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from ros_bridge.robot_node import RobotNode
from ros_bridge.mqtt_bridge import MqttBridge


@pytest.fixture(autouse=True)
def init_rclpy():
    rclpy.init()
    yield
    rclpy.shutdown()


class TestRobotNode:
    def test_creation(self):
        node = RobotNode()
        assert node.robot_id == 1
        assert node.battery == 100.0
        assert node.status == "Moving"
        node.destroy_node()

    def test_custom_parameters(self):
        rclpy.ok()
        node = RobotNode()
        node.destroy_node()

    def test_odom_published(self):
        node = RobotNode()
        received = []

        def callback(msg):
            received.append(msg)

        sub = node.create_subscription(Odometry, "/robot/odom", callback, 10)
        node.simulate_step()
        rclpy.spin_once(node, timeout_sec=0.1)
        assert len(received) > 0
        node.destroy_node()

    def test_battery_published(self):
        node = RobotNode()
        received = []

        def callback(msg):
            received.append(msg)

        sub = node.create_subscription(Float32, "/robot/battery", callback, 10)
        node.simulate_step()
        rclpy.spin_once(node, timeout_sec=0.1)
        assert len(received) > 0
        assert received[0].data == 100.0
        node.destroy_node()

    def test_battery_drains_on_move(self):
        node = RobotNode()
        node.velocity_x = 1.0
        node.battery = 50.0
        node.simulate_step()
        assert node.battery < 50.0
        node.destroy_node()


class TestMqttBridge:
    def test_creation(self):
        node = MqttBridge()
        assert node.robot_id == 1
        node.destroy_node()
