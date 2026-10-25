
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointMonitor(Node):
    def __init__(self):
        super().__init__('joint_monitor')

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.get_logger().info('Joint monitor started. Waiting for joint states...')

    def joint_state_callback(self, msg):
        for name, position in zip(msg.name, msg.position):
            self.get_logger().info(
                f'{name}: {position:.3f} rad'
            )


def main(args=None):
    rclpy.init(args=args)
    node = JointMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
