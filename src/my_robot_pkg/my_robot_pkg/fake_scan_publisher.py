import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class FakeScanPublisher(Node):
    def __init__(self):
        super().__init__('fake_scan_publisher')

        # World geometry: 5m x 5m square room centered on origin.
        # Each wall is a line segment ((ax,ay), (bx,by)) in world coordinates.
        self.walls = [
            ((-2.5, -2.5), ( 2.5, -2.5)),  # south wall
            (( 2.5, -2.5), ( 2.5,  2.5)),  # east  wall
            (( 2.5,  2.5), (-2.5,  2.5)),  # north wall
            ((-2.5,  2.5), (-2.5, -2.5)),  # west  wall
        ]

        # LaserScan parameters — match Turtlebot3 LDS-01 hardware exactly.
        self.num_samples = 360
        self.angle_min = 0.0
        self.angle_max = 2.0 * math.pi
        self.angle_increment = (self.angle_max - self.angle_min) / self.num_samples
        self.range_min = 0.12
        self.range_max = 3.5
        self.publish_period = 0.2  # 5 Hz

        # Robot pose, updated from /odom.
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Best-effort QoS for sensor data (the convention for /scan).
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.scan_pub = self.create_publisher(LaserScan, '/scan', sensor_qos)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        self.timer = self.create_timer(self.publish_period, self.publish_scan)

        self.get_logger().info('fake_scan_publisher up — 4 walls, 5x5m room')

    def odom_callback(self, msg):
        # Sensor callbacks only update state — no work here.
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )

    def cast_ray(self, world_angle):
        """Distance from (self.x, self.y) to nearest wall along world_angle."""
        dx = math.cos(world_angle)
        dy = math.sin(world_angle)
        nearest = self.range_max

        for (ax, ay), (bx, by) in self.walls:
            sx = bx - ax  # segment direction
            sy = by - ay
            det = sx * dy - sy * dx
            if abs(det) < 1e-9:
                continue  # ray parallel to segment
            t = (sx * (ay - self.y) - sy * (ax - self.x)) / det
            u = (dx * (ay - self.y) - dy * (ax - self.x)) / det
            if t >= 0.0 and 0.0 <= u <= 1.0 and t < nearest:
                nearest = t

        return nearest

    def publish_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_scan'
        msg.angle_min = self.angle_min
        msg.angle_max = self.angle_max
        msg.angle_increment = self.angle_increment
        msg.time_increment = 0.0
        msg.scan_time = self.publish_period
        msg.range_min = self.range_min
        msg.range_max = self.range_max

        ranges = []
        for i in range(self.num_samples):
            alpha = self.angle_min + i * self.angle_increment
            world_angle = self.yaw + alpha
            t = self.cast_ray(world_angle)
            ranges.append(t if t >= self.range_min else float('inf'))
        msg.ranges = ranges

        self.scan_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FakeScanPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
