#!/usr/bin/env python3
"""Terminal command source. Accepts degrees; can request explicit clamping."""
import math
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from .sync_common import load_limits, name_for, deg_range, nearest


def main(args=None):
    physical, limits = load_limits()
    rclpy.init(args=args)
    node = Node('tinker_terminal_controller')
    pub = node.create_publisher(String, '/tinker/joint_request', 10)
    def on_status(msg):
        print(f'\n[SUBSCRIBER] {msg.data}', flush=True)
    node.create_subscription(String, '/tinker/status', on_status, 10)
    def on_targets(msg):
        node.targets = dict(zip(msg.name, msg.position))
    node.targets = {}
    node.create_subscription(JointState, '/tinker/joint_targets', on_targets, 10)
    work = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    work.start()
    print('TINKER ARM — TERMINAL CONTROLLER (DEGREES)')
    print('Example: Joint_3 30  |  Joint_2 -20  |  show  |  exit')
    try:
        while rclpy.ok():
            try:
                raw = input('controller (deg)> ').strip()
            except EOFError:
                break
            if raw.lower() in ('exit', 'quit'):
                break
            if raw.lower() == 'show':
                for j, lim in limits.items():
                    current = node.targets.get(j)
                    position = f' | target {math.degrees(current):.1f}°' if current is not None else ''
                    print(f'  {j}: {deg_range(lim)}{position}')
                continue
            fields = raw.split()
            if len(fields) != 2:
                print('Use Joint_3 30  (degrees)')
                continue
            j = name_for(fields[0])
            if j is None:
                print('Unknown joint. Type show.')
                continue
            try:
                deg = float(fields[1])
            except ValueError:
                print('Angle must be a number in degrees.')
                continue
            if not math.isfinite(deg):
                print('Angle must be finite.')
                continue
            radians = math.radians(deg)
            suffix = ''
            if not limits[j][0] <= radians <= limits[j][1]:
                suggested = math.degrees(nearest(radians, limits[j]))
                print(f'OUT OF RANGE: recommended {j} range {deg_range(limits[j])}')
                print(f'1) Go to nearest safe limit: {suggested:.2f}°')
                print('2) Keep current position (do not send)')
                try:
                    choice = input('Choose 1 or 2: ').strip()
                except EOFError:
                    break
                if choice != '1':
                    print('KEEP: command cancelled.')
                    continue
                suffix = ' limit'
            if pub.get_subscription_count() == 0:
                print('NOT SENT: start the Joint Subscriber (sync hub) terminal first.')
                continue
            data = String()
            data.data = f'{j} {deg:.7f}{suffix}'
            pub.publish(data)
            print(f'PUBLISHED: {data.data} degrees')
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
