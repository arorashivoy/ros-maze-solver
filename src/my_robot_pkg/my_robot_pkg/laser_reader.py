import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan


class LaserReader(Node):
    def __init__(self):
        super().__init__('laser_reader')
        scan_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_scan = self.create_subscription(LaserScan, '/scan', self.callback, scan_qos)

    def beam_index(self, scan, angle_rad):
        i = round((angle_rad - scan.angle_min) / scan.angle_increment)
        return i % len(scan.ranges)

    def callback(self, scan):
        i_front = self.beam_index(scan, 0.0)
        i_left  = self.beam_index(scan, math.pi / 2)
        i_right = self.beam_index(scan, -math.pi / 2)
        i_back  = self.beam_index(scan, math.pi)
        
        n = len(scan.ranges)
        half_n = round((math.pi / 6) / scan.angle_increment)
        front_cone = [scan.ranges[(i_front + k) % n] for k in range(-half_n, half_n + 1)]

        valid = [r for r in front_cone if math.isfinite(r) and r >= scan.range_min]
        nearest_front = min(valid) if valid else float('inf')

        self.get_logger().info(
                f'Scan Data:\n\tFront: {scan.ranges[i_front]:.2f}\n\tLeft: {scan.ranges[i_left]:.2f}\n\tBack: {scan.ranges[i_back]:.2f}\n\tRight: {scan.ranges[i_right]:.2f}\n\tMin Dist: {nearest_front:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = LaserReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

