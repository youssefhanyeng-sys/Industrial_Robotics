#!/usr/bin/env python3

import time
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.msg import JointTrajectoryControllerState

JOINTS = (
    'Joint_1', 'Joint_2', 'Joint_3', 'Joint_4',
    'Joint_5', 'Left_Joint', 'Right_Joint'
)

LIMITS = (
    (0.0, 6.27), (-0.85, 0.85), (-1.1, 1.1),
    (0.0, 6.27), (-1.85, 2.2),
    (-0.78, 0.0), (0.0, 0.78)
)


class ReliableSliderBridge(Node):
    def __init__(self):
        super().__init__('reliable_slider_bridge')

        self.actual = {}
        self.targets = {}
        self.last_slider = None
        self.first_slider_time = None
        self.ready = False
        self.dirty = False

        self.pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        self.create_subscription(
            JointTrajectoryControllerState,
            '/joint_trajectory_controller/controller_state',
            self.on_state, 10
        )

        self.create_subscription(
            JointState, '/slider_joint_states',
            self.on_slider, 10
        )

        self.create_timer(0.05, self.tick)
        self.get_logger().info(
            'Bridge waiting for controller feedback and slider initialization...'
        )

    def on_state(self, msg):
        if len(msg.feedback.positions) != len(msg.joint_names):
            return
        self.actual.update(
            dict(zip(msg.joint_names, msg.feedback.positions))
        )

    def on_slider(self, msg):
        incoming = dict(zip(msg.name, msg.position))

        if not all(
            j in incoming and math.isfinite(incoming[j])
            for j in JOINTS
        ):
            return

        if self.first_slider_time is None:
            self.first_slider_time = time.monotonic()

        if not self.ready:
            self.last_slider = incoming
            return

        for j, (lo, hi) in zip(JOINTS, LIMITS):
            if abs(incoming[j] - self.last_slider[j]) > 0.001:
                target = max(lo, min(hi, incoming[j]))
                self.targets[j] = target
                self.dirty = True
                self.get_logger().info(
                    f'{j} target = {target:.3f} rad'
                )

        self.last_slider = incoming

    def tick(self):
        now = time.monotonic()

        if not self.ready:
            if (
                self.first_slider_time is not None
                and now - self.first_slider_time > 1.0
                and all(j in self.actual for j in JOINTS)
                and self.pub.get_subscription_count() > 0
            ):
                self.targets = {
                    j: self.actual[j] for j in JOINTS
                }
                self.ready = True
                self.get_logger().info(
                    'READY: move one slider now; initial centering ignored.'
                )
            return

        if not all(j in self.actual for j in JOINTS):
            return

        if self.pub.get_subscription_count() == 0:
            return

        active = getattr(self, 'command_active', False)
        last = getattr(self, 'last_publish_time', 0.0)

        error = max(
            abs(self.targets[j] - self.actual[j])
            for j in JOINTS
        )

        # Repeat an unachieved target, without needing
        # another slider movement to trigger publication.
        retry = (
            active
            and error > 0.03
            and now - last >= 0.6
        )

        if not self.dirty and not retry:
            return

        trajectory = JointTrajectory()
        trajectory.joint_names = list(JOINTS)

        point = JointTrajectoryPoint()
        point.positions = [
            self.targets[j] for j in JOINTS
        ]
        point.time_from_start.nanosec = 500000000

        trajectory.points = [point]
        self.pub.publish(trajectory)

        self.command_active = True
        self.last_publish_time = now
        self.dirty = False

        if retry:
            self.get_logger().warning(
                f'RETRY: target not reached; max error={error:.3f} rad'
            )
        else:
            self.get_logger().info(
                'SENT: ' + ', '.join(
                    f'{j}={self.targets[j]:.3f}'
                    for j in JOINTS
                )
            )


def main():
    rclpy.init()
    node = ReliableSliderBridge()

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
