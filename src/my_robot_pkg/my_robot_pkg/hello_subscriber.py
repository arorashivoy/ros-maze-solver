import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloSubscriber(Node):
    def __init__(self):
        super().__init__('hello_subscriber')
        self.sub = self.create_subscription(String, '/hello', self.callback, 10)

    def callback(self, msg):
        self.get_logger().info(f'Got Message: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = HelloSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
