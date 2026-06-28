import math
import random

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class NoisyOdomPublisher(Node):
    def __init__(self):
        super().__init__('noisy_odom_publisher')

        self.declare_parameter('sigma_linear', 0.05)   # m drift std per √m traveled
        self.declare_parameter('sigma_angular', 0.03)  # rad drift std per √rad rotated

        self.sigma_lin = self.get_parameter('sigma_linear').value
        self.sigma_ang = self.get_parameter('sigma_angular').value

        # Accumulated drift in world frame
        self.bias_x = 0.0
        self.bias_y = 0.0
        self.bias_th = 0.0

        # Previous clean pose for computing Δs, Δθ
        self.prev_x = None
        self.prev_y = None
        self.prev_th = None

        self.pub = self.create_publisher(Odometry, '/odom_noisy', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.get_logger().info(
            f'noisy_odom_publisher ready — σ_lin={self.sigma_lin}, σ_ang={self.sigma_ang}'
        )

    def odom_callback(self, msg: Odometry):
        q = msg.pose.pose.orientation
        th = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        if self.prev_x is not None:
            ds = math.sqrt((x - self.prev_x) ** 2 + (y - self.prev_y) ** 2)
            dth = abs(th - self.prev_th)
            # Wrap dth to [0, π]
            if dth > math.pi:
                dth = 2.0 * math.pi - dth

            # Random walk: variance grows linearly with distance (√ds scaling)
            if ds > 1e-4:
                self.bias_x += self.sigma_lin * math.sqrt(ds) * random.gauss(0.0, 1.0)
                self.bias_y += self.sigma_lin * math.sqrt(ds) * random.gauss(0.0, 1.0)
            if dth > 1e-5:
                self.bias_th += self.sigma_ang * math.sqrt(dth) * random.gauss(0.0, 1.0)

        self.prev_x = x
        self.prev_y = y
        self.prev_th = th

        noisy_x = x + self.bias_x
        noisy_y = y + self.bias_y
        noisy_th = th + self.bias_th

        # Publish /odom_noisy topic (for fake_scan_publisher to consume)
        noisy_msg = Odometry()
        noisy_msg.header = msg.header
        noisy_msg.header.frame_id = 'odom_noisy'
        noisy_msg.child_frame_id = 'base_footprint_noisy'
        noisy_msg.pose.pose.position.x = noisy_x
        noisy_msg.pose.pose.position.y = noisy_y
        noisy_msg.pose.pose.position.z = 0.0
        # Convert noisy yaw back to quaternion (pure z-rotation)
        noisy_msg.pose.pose.orientation.x = 0.0
        noisy_msg.pose.pose.orientation.y = 0.0
        noisy_msg.pose.pose.orientation.z = math.sin(noisy_th / 2.0)
        noisy_msg.pose.pose.orientation.w = math.cos(noisy_th / 2.0)
        noisy_msg.twist = msg.twist
        self.pub.publish(noisy_msg)

        # Publish TF: odom_noisy → base_footprint_noisy (for SLAM Toolbox)
        tf = TransformStamped()
        tf.header.stamp = msg.header.stamp
        tf.header.frame_id = 'odom_noisy'
        tf.child_frame_id = 'base_footprint_noisy'
        tf.transform.translation.x = noisy_x
        tf.transform.translation.y = noisy_y
        tf.transform.translation.z = 0.0
        tf.transform.rotation.x = 0.0
        tf.transform.rotation.y = 0.0
        tf.transform.rotation.z = math.sin(noisy_th / 2.0)
        tf.transform.rotation.w = math.cos(noisy_th / 2.0)
        self.tf_broadcaster.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = NoisyOdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
