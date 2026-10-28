#!/usr/bin/env python3
"""Friend's joint command GUI: degree inputs, live synchronization, limit prompts."""
import math
import queue
import threading
import tkinter as tk
from tkinter import messagebox
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from .sync_common import JOINTS, load_limits, nearest, deg_range

class FriendGUI(Node):
    def __init__(self):
        super().__init__('tinker_joint_gui_controller')
        _, self.limits = load_limits()
        self.events = queue.Queue()
        self.targets = {}
        self.actual = {}
        self.publisher = self.create_publisher(String, '/tinker/joint_request', 10)
        self.create_subscription(JointState, '/tinker/joint_targets',
                                 lambda m: self.events.put(('targets', dict(zip(m.name, m.position)))), 10)
        self.create_subscription(JointState, '/joint_states',
                                 lambda m: self.events.put(('actual', dict(zip(m.name, m.position)))), 10)
        self.create_subscription(String, '/tinker/status',
                                 lambda m: self.events.put(('status', m.data)), 10)
        self.root = tk.Tk()
        self.root.title('TINKER ARM | Friend GUI (degrees)')
        self.root.geometry('620x510')
        self.root.minsize(550, 450)
        container = tk.Frame(self.root, padx=18, pady=12)
        container.pack(fill='both', expand=True)
        tk.Label(container, text='TINKER ARM — JOINT COMMANDS', font=('Arial', 15, 'bold')).grid(
            row=0, column=0, columnspan=4, pady=(2, 8))
        tk.Label(container, text='Joint', anchor='w').grid(row=1, column=0, sticky='w')
        tk.Label(container, text='Target (deg)').grid(row=1, column=1)
        tk.Label(container, text='Actual (deg)').grid(row=1, column=2)
        tk.Label(container, text='Command').grid(row=1, column=3)
        self.entries = {}
        self.feedback_labels = {}
        for i, j in enumerate(JOINTS, 2):
            tk.Label(container, text=f'{j}\n{deg_range(self.limits[j])}',
                     justify='left').grid(row=i, column=0, sticky='w', padx=5, pady=7)
            field = tk.Entry(container, width=13, justify='center')
            field.insert(0, '—')
            field.grid(row=i, column=1, padx=8)
            field.bind('<Return>', lambda event, joint=j: self.send(joint))
            self.entries[j] = field
            actual = tk.Label(container, text='Waiting...', width=16)
            actual.grid(row=i, column=2, padx=8)
            self.feedback_labels[j] = actual
            tk.Button(container, text='Send', command=lambda joint=j: self.send(joint),
                      padx=12).grid(row=i, column=3, padx=8)
        self.status = tk.Label(container, text='Waiting for controller...', fg='#225588',
                               wraplength=560, justify='left')
        self.status.grid(row=10, column=0, columnspan=4, sticky='w', pady=12)
        tk.Label(container, text='Inputs in DEGREES. Slider GUI stays in radians. '
                  'Only the sync hub publishes to Gazebo.', fg='#555555').grid(
                  row=11, column=0, columnspan=4)
        container.columnconfigure(0, weight=1)
        self.root.after(80, self.process_events)
        self.root.protocol('WM_DELETE_WINDOW', self.root.destroy)

    def process_events(self):
        try:
            for _ in range(250):
                event, payload = self.events.get_nowait()
                if event == 'targets':
                    self.targets = payload
                    focused = self.root.focus_get()
                    for j, entry in self.entries.items():
                        if j in payload and focused is not entry:
                            value = f'{math.degrees(payload[j]):.2f}'
                            if entry.get() != value:
                                entry.delete(0, 'end')
                                entry.insert(0, value)
                elif event == 'actual':
                    self.actual = payload
                    for j, label in self.feedback_labels.items():
                        if j in payload:
                            label.config(text=f'{math.degrees(payload[j]):.2f}°')
                elif event == 'status':
                    self.status.config(text=payload)
        except queue.Empty:
            pass
        try:
            self.root.after(80, self.process_events)
        except tk.TclError:
            pass

    def send(self, joint):
        text = self.entries[joint].get().strip()
        try:
            deg = float(text)
        except ValueError:
            messagebox.showerror('Invalid angle', 'Enter a numeric value in degrees.')
            return
        if not math.isfinite(deg):
            messagebox.showerror('Invalid angle', 'Enter a finite angle.')
            return
        rad = math.radians(deg)
        suffix = ''
        lim = self.limits[joint]
        if not lim[0] <= rad <= lim[1]:
            suggested = math.degrees(nearest(rad, lim))
            to_limit = messagebox.askyesno(
                'Joint angle exceeds recommended safe range',
                f'{joint}: requested {deg:.2f}°.\nRecommended range: {deg_range(lim)}\n\n'
                f'YES = move to nearest safe limit ({suggested:.2f}°)\n'
                f'NO = keep current position (no command)')
            if not to_limit:
                if joint in self.targets:
                    field = self.entries[joint]
                    field.delete(0, 'end')
                    field.insert(0, f'{math.degrees(self.targets[joint]):.2f}')
                self.status.config(text=f'KEPT {joint}: no new movement.')
                return
            suffix = ' limit'
        if self.publisher.get_subscription_count() == 0:
            messagebox.showwarning('Not connected', 'Launch the Joint Subscriber sync hub first.')
            return
        msg = String()
        msg.data = f'{joint} {deg:.7f}{suffix}'
        self.publisher.publish(msg)
        if suffix:
            field = self.entries[joint]
            field.delete(0, 'end')
            field.insert(0, f'{math.degrees(nearest(rad, lim)):.2f}')
        self.root.focus_set()  # Allow the shared target update to refresh this field.
        self.status.config(text=f'SENT {joint}: {deg:.2f}°')


def main(args=None):
    rclpy.init(args=args)
    gui = FriendGUI()
    thread = threading.Thread(target=rclpy.spin, args=(gui,), daemon=True)
    thread.start()
    try:
        gui.root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        gui.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
