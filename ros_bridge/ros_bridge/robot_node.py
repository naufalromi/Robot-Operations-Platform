import math
import random
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from std_msgs.msg import Float32, String, Header
from geometry_msgs.msg import Twist, Quaternion, Point
from nav_msgs.msg import Odometry


TASKS = ["Patrolling", "Inspecting", "Returning to Base", "Scanning Area", "Idle"]
TASK_WEIGHTS = [30, 20, 15, 20, 15]


class RobotNode(Node):
    def __init__(self):
        super().__init__("robot_simulator")

        self.declare_parameter("robot_id", 1)
        self.declare_parameter("initial_x", 0.0)
        self.declare_parameter("initial_y", 0.0)
        self.declare_parameter("initial_battery", 100.0)
        self.declare_parameter("status", "Moving")

        self.robot_id = self.get_parameter("robot_id").value
        self.x = self.get_parameter("initial_x").value
        self.y = self.get_parameter("initial_y").value
        self.battery = self.get_parameter("initial_battery").value
        self.status = self.get_parameter("status").value
        self.task = "Patrolling"
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.heading = 0.0

        self.battery_drain_rate = 0.5
        self.battery_charge_rate = 2.0
        self.move_speed = 1.0
        self.sim_rate = 1.0

        self.is_charging = False
        self.is_stopped = False

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        self.odom_pub = self.create_publisher(Odometry, "/robot/odom", qos)
        self.battery_pub = self.create_publisher(Float32, "/robot/battery", 10)
        self.status_pub = self.create_publisher(String, "/robot/status", 10)

        self.cmd_vel_sub = self.create_subscription(
            Twist, "/robot/cmd_vel", self.cmd_vel_callback, 10
        )

        self.cmd_sub = self.create_subscription(
            String, "/robot/command", self.command_callback, 10
        )

        self.timer = self.create_timer(1.0 / self.sim_rate, self.simulate_step)

        self.get_logger().info(
            f"Robot {self.robot_id} initialized at ({self.x}, {self.y})"
        )

    def cmd_vel_callback(self, msg: Twist):
        if self.is_stopped:
            return
        self.velocity_x = msg.linear.x
        self.velocity_y = msg.linear.y
        self.get_logger().debug(
            f"cmd_vel received: vx={self.velocity_x:.2f} vy={self.velocity_y:.2f}"
        )

    def command_callback(self, msg: String):
        command = msg.data.upper()
        self.get_logger().info(f"Command received: {command}")

        if command == "STOP":
            self.is_stopped = True
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            self.status = "Stopped"
            self.task = "Idle"
            self.get_logger().info("Robot STOPPED")

        elif command == "RESUME":
            self.is_stopped = False
            self.is_charging = False
            self.status = "Moving"
            self.task = random.choices(TASKS, weights=TASK_WEIGHTS, k=1)[0]
            self.get_logger().info("Robot RESUMED")

        elif command == "CHARGE":
            self.is_stopped = False
            self.is_charging = True
            self.status = "Charging"
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            self.get_logger().info("Robot CHARGING")

    def simulate_step(self):
        if self.status == "Broken":
            self.publish_odom()
            self.publish_battery()
            self.publish_status()
            return

        if self.is_charging:
            self.battery = min(100.0, self.battery + self.battery_charge_rate)
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            self.task = "Charging"
            if self.battery >= 100.0:
                self.is_charging = False
                self.status = "Moving"
                self.task = random.choices(TASKS, weights=TASK_WEIGHTS, k=1)[0]
                self.get_logger().info("Battery fully charged, resuming movement")

        elif not self.is_stopped:
            if self.battery <= 0:
                self.status = "Stopped"
                self.task = "Idle"
                self.velocity_x = 0.0
                self.velocity_y = 0.0
                self.get_logger().warn("Battery depleted, robot stopped")
            else:
                if self.velocity_x == 0.0 and self.velocity_y == 0.0:
                    self.random_walk()
                self.x += self.velocity_x * self.sim_rate
                self.y += self.velocity_y * self.sim_rate
                self.battery = max(0.0, self.battery - self.battery_drain_rate)

                if self.velocity_x != 0.0 or self.velocity_y != 0.0:
                    self.heading = math.atan2(self.velocity_y, self.velocity_x)

        self.publish_odom()
        self.publish_battery()
        self.publish_status()

    def random_walk(self):
        dx = random.uniform(-self.move_speed, self.move_speed)
        dy = random.uniform(-self.move_speed, self.move_speed)
        self.velocity_x = dx
        self.velocity_y = dy
        if random.random() < 0.1:
            self.task = random.choices(TASKS, weights=TASK_WEIGHTS, k=1)[0]

    def publish_odom(self):
        msg = Odometry()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "odom"
        msg.child_frame_id = "base_link"

        msg.pose.pose.position = Point(x=self.x, y=self.y, z=0.0)
        q = Quaternion()
        q.z = math.sin(self.heading / 2.0)
        q.w = math.cos(self.heading / 2.0)
        msg.pose.pose.orientation = q

        msg.twist.twist.linear.x = self.velocity_x
        msg.twist.twist.linear.y = self.velocity_y

        self.odom_pub.publish(msg)

    def publish_battery(self):
        msg = Float32()
        msg.data = self.battery
        self.battery_pub.publish(msg)

    def publish_status(self):
        msg = String()
        msg.data = self.task
        self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RobotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
