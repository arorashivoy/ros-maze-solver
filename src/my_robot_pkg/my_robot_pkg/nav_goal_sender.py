import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from rclpy.qos import QoSProfile


WAYPOINTS = [
    (1.0,  0.0, 0.0),   # (x, y, yaw_radians)
    (1.0,  1.0, 1.5708),
    (0.0,  0.0, 0.0),
]


class NavGoalSender(Node):
    def __init__(self):
        super().__init__('nav_goal_sender')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._waypoints = list(WAYPOINTS)
        self._current = 0

        self.get_logger().info('Waiting for navigate_to_pose action server...')
        self._client.wait_for_server()
        self.get_logger().info('Action server ready. Sending first waypoint.')
        self._send_next()

    def _send_next(self):
        if self._current >= len(self._waypoints):
            self.get_logger().info('All waypoints reached.')
            return

        x, y, yaw = self._waypoints[self._current]
        self.get_logger().info(
            f'Waypoint {self._current + 1}/{len(self._waypoints)}: '
            f'x={x}, y={y}, yaw={yaw:.2f} rad'
        )

        goal = NavigateToPose.Goal()
        goal.pose = self._make_pose(x, y, yaw)

        future = self._client.send_goal_async(
            goal,
            feedback_callback=self._on_feedback,
        )
        future.add_done_callback(self._on_goal_accepted)

    def _on_goal_accepted(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by Nav2.')
            return
        self.get_logger().info('Goal accepted.')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

    def _on_feedback(self, feedback_msg):
        d = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'  Distance remaining: {d:.2f} m', throttle_duration_sec=1.0)

    def _on_result(self, future):
        status = future.result().status
        # action_msgs/GoalStatus: 4 = SUCCEEDED, 6 = ABORTED
        if status == 4:
            self.get_logger().info(f'Waypoint {self._current + 1} reached.')
            self._current += 1
            self._send_next()
        else:
            self.get_logger().error(f'Navigation failed with status {status}.')

    def _make_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        # yaw → quaternion: only the z and w components are non-zero for a 2D rotation
        # q = (0, 0, sin(yaw/2), cos(yaw/2))
        import math
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose


def main(args=None):
    rclpy.init(args=args)
    node = NavGoalSender()
    rclpy.spin(node)
    rclpy.shutdown()
