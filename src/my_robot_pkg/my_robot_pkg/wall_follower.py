import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from enum import Enum

DOUBLE = ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE)

class State(Enum):
    FIND_WALL = 0
    FOLLOW_WALL = 1
    TURN_RIGHT = 2


class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')

        self.declare_parameter('desired_wall_dist', 0.3, DOUBLE)
        self.declare_parameter('wall_found_dist', 1.0, DOUBLE)
        self.declare_parameter('front_threshold', 0.4, DOUBLE)
        self.declare_parameter('clear_threshold', 0.6, DOUBLE)
        self.declare_parameter('kp', 2.0, DOUBLE)
        self.declare_parameter('kd', 2.0, DOUBLE)
        self.declare_parameter('max_angular', 0.6, DOUBLE)
        self.declare_parameter('linear_speed', 0.15, DOUBLE)
        self.declare_parameter('turn_speed', 0.5, DOUBLE)
        self.declare_parameter('control_period', 0.1, DOUBLE)

        self.d_star = self.get_parameter('desired_wall_dist').value
        self.wall_found = self.get_parameter('wall_found_dist').value
        self.front_thresh = self.get_parameter('front_threshold').value
        self.clear_thresh = self.get_parameter('clear_threshold').value
        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value
        self.max_angular = self.get_parameter('max_angular').value
        self.v = self.get_parameter('linear_speed').value
        self.omega_turn = self.get_parameter('turn_speed').value
        dt = self.get_parameter('control_period').value

        scan_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.scan_sub = self.create_subscription(LaserScan, '/scan',
                                                 self.scan_callback, scan_qos)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(dt, self.control_loop)

        self.front_dist = float('inf')
        self.left_dist = float('inf')
        self.last_scan_time = None
        self.max_scan_age = 0.3

        self.state = State.FIND_WALL
        self.wall_e = 0.0   # current error: left_dist - d_star
        self.wall_de = 0.0   # derivative of error (m/s), computed per scan

    # ── helpers ──────────────────────────────────────────────────────────

    def beam_index(self, scan, angle_rad):
        i = round((angle_rad - scan.angle_min) / scan.angle_increment)
        return i % len(scan.ranges)

    def zone_min(self, scan, angle_a, angle_b):
        """Minimum valid range in the angular zone [angle_a, angle_b] (radians)."""
        ia = self.beam_index(scan, angle_a)
        ib = self.beam_index(scan, angle_b)
        n = len(scan.ranges)
        if ia <= ib:
            indices = range(ia, ib + 1)
        else:
            indices = list(range(ia, n)) + list(range(0, ib + 1))
        valid = [scan.ranges[i] for i in indices
                 if math.isfinite(scan.ranges[i]) and scan.ranges[i] >= scan.range_min]
        return min(valid) if valid else float('inf')

    def stop_robot(self):
        self.cmd_pub.publish(Twist())
        self.get_logger().info('Sent stop command')

    # ── callbacks ─────────────────────────────────────────────────────────

    def scan_callback(self, scan):
        self.front_dist = self.zone_min(scan, -math.pi / 9, math.pi / 9)   # ±20°
        self.left_dist = self.zone_min(scan, math.pi / 3, 2 * math.pi / 3)

        now = self.get_clock().now()
        e_new = self.left_dist - self.d_star
        if self.last_scan_time is not None:
            dt_scan = (now - self.last_scan_time).nanoseconds * 1e-9
            if dt_scan > 0.0:
                self.wall_de = (e_new - self.wall_e) / dt_scan
        self.wall_e = e_new
        self.last_scan_time = now

    def control_loop(self):
        cmd = Twist()

        if self.last_scan_time is None:
            self.cmd_pub.publish(cmd)
            return
        age = (self.get_clock().now() - self.last_scan_time).nanoseconds * 1e-9
        if age > self.max_scan_age:
            self.cmd_pub.publish(cmd)
            return

        if self.state == State.FIND_WALL:
            cmd.linear.x = self.v
            if self.left_dist < self.wall_found:
                self.get_logger().info('Wall found → FOLLOW_WALL')
                self.state = State.FOLLOW_WALL

        elif self.state == State.FOLLOW_WALL:
            if self.front_dist < self.front_thresh:
                self.get_logger().info('Front blocked → TURN_RIGHT')
                self.state = State.TURN_RIGHT
            else:
                raw = self.kp * self.wall_e + self.kd * self.wall_de
                cmd.linear.x = self.v
                cmd.angular.z = max(-self.max_angular, min(self.max_angular, raw))

        elif self.state == State.TURN_RIGHT:
            if self.front_dist > self.clear_thresh:
                self.get_logger().info('Front clear → FOLLOW_WALL')
                self.state = State.FOLLOW_WALL
            else:
                cmd.angular.z = -self.omega_turn

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_robot()
    finally:
        node.destroy_node()
        rclpy.shutdown()
