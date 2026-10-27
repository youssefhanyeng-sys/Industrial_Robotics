#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.msg import JointTrajectoryControllerState


# Performance settings
COMMAND_INTERVAL = 0.03
MOVEMENT_DURATION = 0.15
MINIMUM_CHANGE = 0.001


class FastSliderBridge(Node):

    def __init__(self):
        super().__init__('fast_slider_bridge')

        self.joints = []
        self.targets = {}
        self.actual = {}
        self.last_sent = {}
        self.dirty = False

        # Keep only the newest message to avoid old commands
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.create_subscription(
            JointTrajectoryControllerState,
            '/joint_trajectory_controller/controller_state',
            self.controller_callback,
            qos
        )

        self.create_subscription(
            JointState,
            '/joint_states',
            self.actual_callback,
            qos
        )

        self.create_subscription(
            JointState,
            '/slider_joint_states',
            self.slider_callback,
            qos
        )

        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            qos
        )

        self.create_timer(
            COMMAND_INTERVAL,
            self.send_command
        )

        self.get_logger().info(
            'Fast slider bridge running!'
        )

    def controller_callback(self, msg):
        if msg.joint_names:
            self.joints = list(msg.joint_names)

    def actual_callback(self, msg):
        self.actual.update(
            zip(msg.name, msg.position)
        )

    def slider_callback(self, msg):
        incoming = dict(zip(msg.name, msg.position))

        changed = False

        for joint, position in incoming.items():
            if joint not in self.targets or abs(
                self.targets[joint] - position
            ) > MINIMUM_CHANGE:

                self.targets[joint] = position
                changed = True

        if changed:
            self.dirty = True

    def send_command(self):

        if not self.joints or not self.dirty:
            return

        if not all(
            j in self.targets or j in self.actual
            for j in self.joints
        ):
            return

        positions = [
            self.targets.get(
                j, self.actual.get(j, 0.0)
            )
            for j in self.joints
        ]

        # Avoid sending duplicate trajectories
        if self.last_sent == dict(zip(self.joints, positions)):
            self.dirty = False
            return

        trajectory = JointTrajectory()
        trajectory.joint_names = self.joints

        point = JointTrajectoryPoint()
        point.positions = positions

        duration_ns = int(MOVEMENT_DURATION * 1e9)

        point.time_from_start.sec = duration_ns // 1000000000
        point.time_from_start.nanosec = duration_ns % 1000000000

        trajectory.points = [point]

        self.publisher.publish(trajectory)

        self.last_sent = dict(zip(self.joints, positions))
        self.dirty = False


def main():
    rclpy.init()

    node = FastSliderBridge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
