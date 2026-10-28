# Industrial Robotics — ROS 2 Robotic Arm Simulation

A robotic arm simulation project using **ROS 2 Jazzy, RViz 2, and Gazebo Sim**.

The project includes a robot URDF model, joint controllers, Gazebo physics simulation, and a Python bridge that allows joint sliders to control the simulated robot while RViz visualizes its movement.

## Features

- Robotic arm visualization in RViz 2
- Gazebo physics simulation
- ROS 2 joint trajectory control
- Seven joint sliders, including gripper joints
- Live synchronization of simulated joint positions with RViz
- Low-latency Python slider-to-Gazebo bridge
- Configurable joint movement duration

## Requirements

Tested with:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Gazebo Sim 8
- Python 3
- colcon

Install the required ROS packages:

```bash
sudo apt update
sudo apt install -y \
  git python3-colcon-common-extensions \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-rviz2 \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-xacro
```

## Installation

Clone the repository:

```bash
cd ~
git clone https://github.com/youssefhanyeng-sys/Industrial_Robotics.git
cd Industrial_Robotics
```

Build the workspace:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launching the Complete Simulation

The full interactive simulation uses four terminals.

### Terminal 1 — Launch Gazebo

```bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:${GZ_SIM_RESOURCE_PATH}"

ros2 launch URDF_FIN gazebo.launch.py
```

This starts the Gazebo environment, spawns the robotic arm, and attempts to activate the joint controllers.

Verify that the robot is visible in Gazebo.

### Terminal 2 — Launch RViz

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash

ros2 run rviz2 rviz2 \
  -d ~/Industrial_Robotics/src/URDF_FIN/config/urdf.rviz \
  --ros-args -p use_sim_time:=true
```

RViz displays the robot using joint states and transforms from Gazebo.

**Important:** Do not simultaneously launch `display.launch.py`, because it starts an additional joint-state publisher that can interfere with Gazebo feedback.

### Terminal 3 — Start the Slider Bridge

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash

python3 ~/Industrial_Robotics/src/URDF_FIN/scripts/slider_bridge.py
```

The Python bridge subscribes to slider commands and publishes joint trajectories to the Gazebo controller.

### Terminal 4 — Open the Joint Sliders

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash

ros2 run joint_state_publisher_gui joint_state_publisher_gui \
  --ros-args -r /joint_states:=/slider_joint_states
```

The slider window allows interactive control of the robot's joints.

Moving the sliders sends desired joint positions through the bridge to Gazebo, while RViz displays the resulting simulated robot motion.

## How Synchronization Works

```text
     Joint Slider GUI
            |
            | /slider_joint_states
            v
      Python Bridge
            |
            | /joint_trajectory_controller/joint_trajectory
            v
     ROS 2 Controller
            |
            v
     Gazebo Simulation
            |
            | /joint_states and TF
            v
      RViz Visualization
```

Gazebo is the source of the simulated robot's joint positions. RViz displays those positions rather than independently controlling the physics simulation.

## Performance Tuning

The bridge includes configurable movement settings:

```python
COMMAND_INTERVAL = 0.03
MOVEMENT_DURATION = 0.15
MINIMUM_CHANGE = 0.001
```

- `COMMAND_INTERVAL`: Time between bridge command checks, in seconds.
- `MOVEMENT_DURATION`: Requested duration for each joint trajectory.
- `MINIMUM_CHANGE`: Smallest joint position change that triggers an update, in radians.

For smoother movement, increase `MOVEMENT_DURATION` to `0.30`.

For more responsive movement, try `0.08`, although this may cause jerky motion.

Actual response time depends on simulation performance and controller behavior.

## Verify the Controllers

With Gazebo running, execute:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash

ros2 control list_controllers
```

Expected active controllers:

```text
joint_state_broadcaster       active
joint_trajectory_controller   active
```

## Troubleshooting

### Gazebo is running, but the arm is invisible

Set the Gazebo resource path before launching:

```bash
export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:${GZ_SIM_RESOURCE_PATH}"
```

This helps Gazebo resolve the STL mesh files referenced by the robot description.

### Robot description YAML parsing error

In `gazebo.launch.py`, the robot description must be explicitly treated as a string:

```python
from launch_ros.parameter_descriptions import ParameterValue

robot_description = ParameterValue(
    Command(['xacro ', urdf_file]),
    value_type=str
)
```

### Joint controllers fail to configure

Check for previously running simulations and controller managers. Avoid launching duplicate instances of the simulation.

### Joint sliders are missing

Launch the GUI separately using the Terminal 4 command above.

### Large movement delays

Try tuning the trajectory duration and check Gazebo's real-time factor. A slow simulation can cause joint movement to lag.

## RViz-Only Visualization

To open RViz with its own joint-state GUI, without Gazebo:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 launch URDF_FIN display.launch.py
```

Use this standalone mode only when the Gazebo simulation is not running.

## Project Structure

```text
Industrial_Robotics/
├── src/
│   ├── URDF_FIN/
│   │   ├── config/
│   │   ├── launch/
│   │   │   ├── display.launch.py
│   │   │   └── gazebo.launch.py
│   │   ├── meshes/
│   │   ├── scripts/
│   │   │   └── slider_bridge.py
│   │   ├── urdf/
│   │   └── package.xml
│   └── tinker_robot/
├── README.md
└── .gitignore
```

The ROS build directories (`build`, `install`, and `log`) are generated locally and should not be committed.

## Notes

This is a simulation-oriented project. The Python slider bridge is intended for interactive testing rather than safety-critical real-time control.

The controller's supported joints and joint limits determine which slider commands can be executed successfully.

---

**Industrial Robotics — ROS 2 Jazzy | RViz 2 | Gazebo Sim**

<!-- BEGIN TINKER_ARM_SYNC_DOCS -->
## 🤖 TINKER_ARM — Three synchronized joint-control modes

TINKER_ARM is a seven-joint robot arm simulation built with **ROS 2 Jazzy**, **Gazebo Harmonic** and **RViz 2**. Three control interfaces share one joint target state and move the same robot:

| Mode | Interface | Units | Executable |
| --- | --- | --- | --- |
| 1 | Interactive terminal commands | **Degrees** | `ros2 run tinker_robot controller_publisher` |
| 2 | Joint command Tkinter GUI | **Degrees** | `ros2 run tinker_robot joint_gui_controller` |
| 3 | Original `joint_state_publisher_gui` sliders (shown alongside RViz) | **Radians** | `ros2 run joint_state_publisher_gui joint_state_publisher_gui ...` |

Moving a joint from any one interface updates the shared target and the other control interfaces. **Only the synchronization hub** (`joint_command_subscriber`) publishes trajectory commands to the Gazebo controller. RViz displays joint-state feedback from the simulation.

### System requirements

- Ubuntu 24.04 (native or WSL2) and ROS 2 Jazzy
- Gazebo Harmonic / Gazebo Sim 8, RViz 2, `ros2_control` and `gz_ros2_control`
- Python 3 with `rclpy`, `tkinter`, and the ROS 2 message packages declared in `src/tinker_robot/package.xml`
- `joint_state_publisher_gui` and `colcon`

If the Tkinter GUI is missing on Ubuntu, install `python3-tk` using your package manager. Install remaining ROS dependencies for your distribution as necessary.

### Project files

```text
Industrial_Robotics/
├── src/
│   ├── URDF_FIN/
│   │   ├── urdf/URDF_FIN.urdf
│   │   ├── config/urdf.rviz
│   │   └── launch/gazebo.launch.py
│   └── tinker_robot/
│       ├── setup.py
│       ├── package.xml
│       └── tinker_robot/
│           ├── sync_common.py                # Joint names and conservative limits
│           ├── joint_command_subscriber.py   # Single synchronization/trajectory hub
│           ├── controller_publisher.py       # Interactive terminal commands
│           ├── joint_gui_controller.py       # Degree-entry GUI with live feedback
│           └── joint_monitor.py
└── README.md
```

### Build the workspace

```bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables tinker_robot
```

The executable list should include `joint_command_subscriber`, `controller_publisher`, `joint_gui_controller`, and `joint_monitor`.

### Start the synchronized system — six terminals

Start the processes **in order** and leave them running. Wait until the Gazebo controllers are active before sending joint commands.

**Terminal 1 — Gazebo simulation**

```bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:$HOME/Industrial_Robotics/install/URDF_FIN/share:${GZ_SIM_RESOURCE_PATH}"
ros2 launch URDF_FIN gazebo.launch.py
```

**Terminal 2 — RViz visualization**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run rviz2 rviz2 \
  -d ~/Industrial_Robotics/src/URDF_FIN/config/urdf.rviz \
  --ros-args -p use_sim_time:=true
```

**Terminal 3 — Central synchronization hub (required)**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot joint_command_subscriber
```

Wait for `READY: all seven controller joints detected; synchronized modes enabled.`

**Terminal 4 — Original ROS joint sliders (radians)**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run joint_state_publisher_gui \
  joint_state_publisher_gui \
  --ros-args \
  -r /joint_states:=/slider_joint_states \
  -p source_list:="['/tinker/joint_sync']"
```

**Terminal 5 — Interactive terminal commands (degrees)**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot controller_publisher
```

At the `controller (deg)>` prompt try:

```text
Joint_3 25
Joint_2 -20
Joint_4 90
show
exit
```

**Terminal 6 — Joint command GUI (degrees)**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot joint_gui_controller
```

The GUI shows commanded target angles and actual joint feedback in degrees. Enter a value for one joint and press **Send** (or Enter). The remaining joint targets are preserved.

> **Do not** run the legacy `src/URDF_FIN/scripts/slider_bridge.py`, the previous standalone terminal subscriber, or `display.launch.py` simultaneously with this synchronized system. They may create conflicting publishers, robot state publishers, or joint commands.

### Command safety and units

- Terminal and Tkinter GUI: **degrees**. ROS messages and the original `joint_state_publisher_gui`: **radians**.
- Command text format: `Joint_3 25` (joint name followed by an angle in degrees). Joint names are case-insensitive in the terminal input; canonical names are `Joint_1` through `Joint_5`, `Left_Joint`, `Right_Joint`.
- For out-of-range terminal commands, choose **1 — nearest recommended safe limit** or **2 — keep the current target**. In the GUI, **Yes** clamps to the nearest recommended limit; **No** cancels the command.
- The original ROS slider uses its original radian display; the hub clamps its requested joint target when outside the recommended motion interval.
- Safety limits are calculated from `URDF_FIN.urdf` with additional conservative caps in `src/tinker_robot/tinker_robot/sync_common.py`. The currently configured Joint 3 cap is **−1.0 to +1.0 rad**, avoiding the hard-limit lockups observed at the mechanical endpoints.
- These are **simulation software limits**, not a substitute for hardware motion limits, collision checking or an emergency-stop system.

### ROS topic architecture

```text
Terminal (deg) ───────┐
                      ├── /tinker/joint_request [std_msgs/String]
Tkinter GUI (deg) ────┘                │
                                      ▼
Original ROS slider ─ /slider_joint_states [sensor_msgs/JointState]
                                      │
                                      ▼
                      joint_command_subscriber
                          (single command hub)
                                      │
                         JointTrajectory command
                                      ▼
                 /joint_trajectory_controller/joint_trajectory
                                      │
                                      ▼
                   Gazebo / gz_ros2_control / robot
                                      │
                 /joint_states and /controller_state feedback
                                      │
                   ├── RViz robot visualization
                   ├── GUI actual-position readout
                   └── hub state tracking

Hub → /tinker/joint_targets → Tkinter GUI + terminal target display
Hub → /tinker/joint_sync    → original ROS slider source_list
Hub → /tinker/status        → command outcomes and feedback logs
```

### Troubleshooting

Check the controllers:

```bash
ros2 control list_controllers
```

Both `joint_trajectory_controller` and `joint_state_broadcaster` should be `active`.

Inspect the synchronized joint targets or the command publisher count:

```bash
ros2 topic echo /tinker/joint_targets --once
ros2 topic info -v /joint_trajectory_controller/joint_trajectory
```

The trajectory topic should have **one** user command publisher, the synchronization hub. If your sliders do not follow terminal or GUI changes, verify that Terminal 4 includes `source_list` and the `/slider_joint_states` remapping. If a joint stops at its maximum position, avoid exact URDF hard limits and use the conservative configured range.

### Development notes

This controller layer is designed for simulation and is a step toward adding command sources such as an ESP32 without changing the downstream Gazebo trajectory interface. The three existing control modes should be tested after modifying joint limits, robot geometry, or `ros2_control` parameters.
<!-- END TINKER_ARM_SYNC_DOCS -->
