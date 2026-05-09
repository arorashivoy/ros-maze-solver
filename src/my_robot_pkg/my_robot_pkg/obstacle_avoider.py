import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

DOUBLE = ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE)


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')

        self.declare_parameter('safe_distance', 0.5, DOUBLE)
        self.declare_parameter('v_forward', 0.5, DOUBLE)
        self.declare_parameter('omega_turn', 0.5, DOUBLE)
        self.declare_parameter('control_period', 0.1, DOUBLE)

        self.control_period = float(self.get_parameter('control_period').value)
        self.safe_distance = float(self.get_parameter('safe_distance').value)
        self.v_forward = float(self.get_parameter('v_forward').value)
        self.omega_turn = float(self.get_parameter('omega_turn').value)

        scan_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        vel_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, scan_qos)
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', vel_qos)
        self.timer = self.create_timer(self.control_period, self.publish_vel)

        self.nearest_front = float('inf')
        self.last_scan_time = None
        self.max_scan_age = 0.2

    def beam_index(self, scan, angle_rad):
        i = round((angle_rad - scan.angle_min) / scan.angle_increment)
        return i % len(scan.ranges)

    def scan_callback(self, scan):
        i_front = self.beam_index(scan, 0.0)
        n = len(scan.ranges)
        half_n = round((math.pi / 6) / scan.angle_increment)
        front_cone = [scan.ranges[(i_front + k) % n] for k in range(-half_n, half_n + 1)]

        valid = [r for r in front_cone if math.isfinite(r) and r >= scan.range_min]
        self.nearest_front = min(valid) if valid else float('inf')
        self.last_scan_time = self.get_clock().now()

        self.get_logger().info(f'[{self.last_scan_time}] Nearest Front: {self.nearest_front}')

    def publish_vel(self):
        now = self.get_clock().now()
        if self.last_scan_time is None:
            self.vel_pub.publish(Twist())
            return

        age = (now - self.last_scan_time).nanoseconds * 1e-9    # seconds
        if age > self.max_scan_age:
            self.vel_pub.publish(Twist())
            return


        if self.nearest_front < self.safe_distance:
            cmd = Twist()
            cmd.angular.z = self.omega_turn

            self.vel_pub.publish(cmd)
            return

        cmd = Twist()
        cmd.linear.x = self.v_forward
        self.vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
