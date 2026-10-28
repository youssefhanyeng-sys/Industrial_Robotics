#!/usr/bin/env python3
"""Single command arbiter; only this node publishes trajectories to Gazebo."""
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.msg import JointTrajectoryControllerState
from .sync_common import JOINTS, load_limits, nearest, name_for, deg_range

SLIDER_CHANGE = 0.004  # slider quantization/radians

class SyncedController(Node):
    def __init__(self):
        super().__init__('tinker_synced_controller')
        self.physical, self.safe = load_limits()
        self.targets = None
        self.actual = {}
        self.reference = {}
        self.last_slider = None
        self.block_slider_until = 0.0
        self.last_feedback_log = 0.0
        self.watch = None
        self.trajectory_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.sync_pub = self.create_publisher(JointState, '/tinker/joint_sync', 10)
        self.target_pub = self.create_publisher(JointState, '/tinker/joint_targets', 10)
        self.status_pub = self.create_publisher(String, '/tinker/status', 10)
        self.create_subscription(
            JointTrajectoryControllerState, '/joint_trajectory_controller/controller_state',
            self.on_state, 10)
        self.create_subscription(String, '/tinker/joint_request', self.on_request, 10)
        self.create_subscription(JointState, '/slider_joint_states', self.on_slider, 10)
        self.create_timer(0.5, self.timer)
        self.say('SYNC HUB started. Waiting for Gazebo controller feedback.')
        for j in JOINTS:
            self.get_logger().info(f'{j}: recommended {deg_range(self.safe[j])}')

    def say(self, message):
        self.get_logger().info(message)
        s = String()
        s.data = message
        self.status_pub.publish(s)

    def on_state(self, msg):
        if len(msg.joint_names) != len(msg.feedback.positions):
            return
        self.actual = dict(zip(msg.joint_names, msg.feedback.positions))
        if len(msg.joint_names) == len(msg.reference.positions):
            self.reference = dict(zip(msg.joint_names, msg.reference.positions))
        if self.targets is None and all(j in self.actual for j in JOINTS):
            self.targets = {j: self.actual[j] for j in JOINTS}
            self.say('READY: all seven controller joints detected; synchronized modes enabled.')
            self.publish_sync()
            self.publish_targets()

    def publish_sync(self):
        if self.targets is None:
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINTS)
        msg.position = [float(self.targets[j]) for j in JOINTS]
        self.sync_pub.publish(msg)

    def publish_targets(self):
        if self.targets is None:
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINTS)
        msg.position = [float(self.targets[j]) for j in JOINTS]
        self.target_pub.publish(msg)

    def publish_trajectory(self, origin):
        if self.targets is None:
            return
        if self.trajectory_pub.get_subscription_count() == 0:
            self.say('ERROR: Gazebo trajectory controller is not subscribed; command not sent.')
            return
        traj = JointTrajectory()
        traj.joint_names = list(JOINTS)
        pt = JointTrajectoryPoint()
        pt.positions = [float(self.targets[j]) for j in JOINTS]
        pt.time_from_start.sec = 1
        traj.points = [pt]
        self.trajectory_pub.publish(traj)
        self.publish_targets()
        self.say(f'{origin}: trajectory sent to Gazebo.')

    def on_request(self, msg):
        # Human-entered terminal/Tk commands are DEGREES: Joint_3 30 [limit]
        fields = msg.data.strip().split()
        if len(fields) not in (2, 3):
            self.say('REJECTED: use Joint_3 30 [limit] (degrees).')
            return
        j = name_for(fields[0])
        if j is None:
            self.say(f'REJECTED: unknown joint {fields[0]!r}')
            return
        try:
            deg = float(fields[1])
        except ValueError:
            self.say(f'REJECTED: {j}: angle is not a number.')
            return
        if not math.isfinite(deg):
            self.say(f'REJECTED: {j}: non-finite angle.')
            return
        clamp_requested = len(fields) == 3 and fields[2].lower() == 'limit'
        if len(fields) == 3 and not clamp_requested:
            self.say('REJECTED: optional third token must be limit.')
            return
        if self.targets is None:
            self.say('NOT READY: start Gazebo and wait for controller feedback.')
            return
        angle = math.radians(deg)
        lo, hi = self.safe[j]
        if not lo <= angle <= hi:
            recommendation = math.degrees(nearest(angle, self.safe[j]))
            if not clamp_requested:
                self.say(
                    f'OUT OF RANGE: {j} requested {deg:.2f}°; recommended safe range '
                    f'{deg_range(self.safe[j])}. Choose nearest {recommendation:.2f}° '
                    'or keep existing position. NO movement was made.')
                return
            angle = nearest(angle, self.safe[j])
            self.say(f'CLAMPED: {j}: requested {deg:.2f}° -> {math.degrees(angle):.2f}°')
        if abs(angle - self.targets[j]) < 0.0001:
            self.publish_sync()
            self.publish_targets()
            self.say(f'UNCHANGED: {j} already at target {math.degrees(angle):.2f}°')
            return
        self.targets[j] = angle
        self.block_slider_until = time.monotonic() + 0.8
        self.watch = j
        self.publish_trajectory(f'COMMAND {j}={math.degrees(angle):.2f}°')
        self.publish_sync()

    def on_slider(self, msg):
        incoming = dict(zip(msg.name, msg.position))
        if self.targets is None or not all(j in incoming for j in JOINTS):
            return
        if any(not math.isfinite(incoming[j]) for j in JOINTS):
            return
        if self.last_slider is None:
            self.last_slider = incoming
            # Reset the original JSP GUI centered startup sliders to actual Gazebo targets.
            self.publish_sync()
            return
        prev = self.last_slider
        self.last_slider = incoming
        if time.monotonic() < self.block_slider_until:
            return
        changed = []
        capped = []
        for j in JOINTS:
            if (abs(incoming[j] - prev.get(j, incoming[j])) > SLIDER_CHANGE
                    and abs(incoming[j] - self.targets[j]) > SLIDER_CHANGE):
                value = nearest(incoming[j], self.safe[j])
                if abs(value - incoming[j]) > 1e-6:
                    capped.append(j)
                if abs(value - self.targets[j]) > SLIDER_CHANGE:
                    self.targets[j] = value
                    changed.append(j)
        if not changed and not capped:
            return
        if changed:
            self.watch = changed[-1]
            self.publish_trajectory('SLIDER ' + ', '.join(
                f'{j}={math.degrees(self.targets[j]):.1f}°' for j in changed))
        # Do not feed ordinary slider movements back at every drag step (fights input).
        if capped:
            self.say('SLIDER SAFE LIMIT: clamped ' + ', '.join(capped))
            self.publish_sync()

    def timer(self):
        if self.targets is None:
            return
        self.publish_targets()  # Tk GUI gets current targets even if opened later.
        if self.watch is None or self.watch not in self.actual:
            return
        now = time.monotonic()
        if now - self.last_feedback_log < 1.0:
            return
        self.last_feedback_log = now
        j = self.watch
        target, actual = self.targets[j], self.actual[j]
        ref = self.reference.get(j, float('nan'))
        self.get_logger().info(
            f'FEEDBACK {j}: target={math.degrees(target):.1f}°, '
            f'reference={math.degrees(ref):.1f}°, actual={math.degrees(actual):.1f}°')
        if abs(actual - target) < 0.025:
            self.say(f'TARGET REACHED: {j} = {math.degrees(actual):.1f}°')
            self.watch = None


def main(args=None):
    rclpy.init(args=args)
    node = SyncedController()
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
