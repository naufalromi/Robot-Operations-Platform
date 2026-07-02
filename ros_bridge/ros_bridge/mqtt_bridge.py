import json
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from std_msgs.msg import Float32, String
from nav_msgs.msg import Odometry

import paho.mqtt.client as mqtt

from .config import (
    MQTT_BROKER,
    MQTT_PORT,
    DEFAULT_ROBOT_ID,
)


class MqttBridge(Node):
    def __init__(self):
        super().__init__("mqtt_bridge")

        self.declare_parameter("robot_id", DEFAULT_ROBOT_ID)
        self.declare_parameter("mqtt_broker", MQTT_BROKER)
        self.declare_parameter("mqtt_port", MQTT_PORT)

        self.robot_id = self.get_parameter("robot_id").value
        self.mqtt_broker = self.get_parameter("mqtt_broker").value
        self.mqtt_port = self.get_parameter("mqtt_port").value

        self.telemetry_topic = f"fleet/robot/{self.robot_id}/telemetry"
        self.command_topic = f"fleet/robot/{self.robot_id}/command"

        self.latest_x = 0.0
        self.latest_y = 0.0
        self.latest_battery = 100.0
        self.latest_task = "Idle"
        self.telemetry_changed = False

        self.setup_mqtt()

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        self.odom_sub = self.create_subscription(
            Odometry, "/robot/odom", self.odom_callback, qos
        )
        self.battery_sub = self.create_subscription(
            Float32, "/robot/battery", self.battery_callback, 10
        )
        self.status_sub = self.create_subscription(
            String, "/robot/status", self.status_callback, 10
        )

        self.cmd_vel_pub = self.create_publisher(String, "/robot/command", 10)

        self.telemetry_timer = self.create_timer(0.5, self.publish_telemetry)

        self.get_logger().info(
            f"MQTT Bridge started for robot {self.robot_id} "
            f"(broker: {self.mqtt_broker}:{self.mqtt_port})"
        )

    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_thread = threading.Thread(
                target=self.mqtt_client.loop_forever, daemon=True
            )
            self.mqtt_thread.start()
            self.get_logger().info("MQTT client connected")
        except Exception as e:
            self.get_logger().error(f"MQTT connection failed: {e}")

    def on_mqtt_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.get_logger().info(f"Subscribed to {self.command_topic}")
            client.subscribe(self.command_topic)
        else:
            self.get_logger().error(f"MQTT connect failed: {reason_code}")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            command = payload.get("command", "")

            self.get_logger().info(f"MQTT command received: {command}")

            cmd_msg = String()
            cmd_msg.data = command
            self.cmd_vel_pub.publish(cmd_msg)

        except Exception as e:
            self.get_logger().error(f"Error processing MQTT message: {e}")

    def odom_callback(self, msg: Odometry):
        self.latest_x = msg.pose.pose.position.x
        self.latest_y = msg.pose.pose.position.y
        self.telemetry_changed = True

    def battery_callback(self, msg: Float32):
        self.latest_battery = msg.data
        self.telemetry_changed = True

    def status_callback(self, msg: String):
        self.latest_task = msg.data
        self.telemetry_changed = True

    def publish_telemetry(self):
        if not self.telemetry_changed and self.latest_task == "Idle":
            return

        payload = {
            "id": self.robot_id,
            "x": round(self.latest_x, 2),
            "y": round(self.latest_y, 2),
            "battery": round(self.latest_battery, 1),
            "task": self.latest_task,
        }

        try:
            self.mqtt_client.publish(
                self.telemetry_topic, json.dumps(payload), qos=1
            )
            self.telemetry_changed = False
        except Exception as e:
            self.get_logger().error(f"Failed to publish telemetry: {e}")

    def destroy_node(self):
        self.mqtt_client.disconnect()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MqttBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
