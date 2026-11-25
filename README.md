# Industrial Robotics — ROS 2 Robotic Arm Simulation

A robotic arm simulation project using **ROS 2 Jazzy, RViz 2, Gazebo Harmonic, and MoveIt 2**.

The project includes a robot URDF model, joint controllers, Gazebo physics simulation, and a Python bridge that allows joint sliders to control the simulated robot while RViz visualizes its movement.

## Choose a launch mode

| Mode | Terminals | Use it for |
| --- | ---: | --- |
| [Gazebo + MoveIt 2 only](#gazebo--moveit-2-only-two-terminals) | 2 | Motion planning and named arm/gripper poses; recommended for MoveIt testing |
| [Synchronized manual control](#start-the-synchronized-system--six-terminals) | 6 | Sliders, terminal commands and Tkinter GUI |
| [Full system with MoveIt 2](#tinker_arm--seven-terminal-launch-six-existing-processes--moveit-2) | 7 | All manual interfaces plus MoveIt |
| [RViz only](#rviz-only-visualization) | 1 | Visualization without Gazebo |
| [Legacy slider bridge](#legacy-slider-bridge-four-terminals) | 4 | Older manual control workflow |

Choose **one** mode per session. Do not start another Gazebo instance or a second MoveIt action server.

## Features

- Robotic arm visualization in RViz 2
- Gazebo physics simulation
- ROS 2 joint trajectory control
- Seven joint sliders, including gripper joints
- Live synchronization of simulated joint positions with RViz
- Low-latency Python slider-to-Gazebo bridge
- Configurable joint movement duration
- MoveIt 2 motion planning and execution for the arm and gripper
- Named robot poses and a permanent MoveIt launch file

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
  ros-jazzy-xacro \
  ros-jazzy-moveit python3-tk
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

## Gazebo + MoveIt 2 only (two terminals)

This is the simplest mode for planning and executing arm or gripper poses, and the recommended starting point when troubleshooting MoveIt. Build the workspace using the installation steps above before launching.

### Terminal 1 — Gazebo

~~~bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:$HOME/Industrial_Robotics/install/URDF_FIN/share:${GZ_SIM_RESOURCE_PATH}"

ros2 launch URDF_FIN gazebo.launch.py
~~~

Wait until the robot appears and both controllers are active. Keep this terminal running.

### Terminal 2 — MoveIt 2 + MoveIt RViz

~~~bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch tinker_moveit_config terminal7.launch.py
~~~

This is the same permanent launcher used by Terminal 7 in the full system. It starts `move_group` and MoveIt RViz with simulation time enabled. It does not start Gazebo again.

Do not start the standalone RViz window, synchronization hub, sliders, terminal controller or Tkinter GUI in this mode.

### Use MoveIt

1. Open the **MotionPlanning** panel.
2. Select `arm_group` (five arm joints) or `hand_group` (two gripper joints).
3. Set **Start State** to `<current>`.
4. Select a named **Goal State** different from the current pose.
5. For initial tests, set velocity and acceleration scaling to `0.2`.
6. Click **Plan**. If planning succeeds and the path looks correct, click **Execute**. Alternatively, use **Plan & Execute** for a fresh plan.

Named poses currently in the repository:

| Planning group | Saved poses |
| --- | --- |
| `arm_group` | `zero_pose`, `JOE_POSE`, `DINA_POSE`, `AW_POSE`, `NATALIE_POSE` |
| `hand_group` | `open_hand`, `half_open_hand`, `close_hand` |

The names are defined in [URDF_FIN.srdf](src/tinker_moveit_config/config/URDF_FIN.srdf). A saved pose still needs to pass collision and joint-limit checks before execution.

## Legacy slider bridge (four terminals)

This is the older interactive simulation workflow. Use it separately from the six- and seven-terminal modes.

### Terminal 1 — Launch Gazebo

```bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:$HOME/Industrial_Robotics/install/URDF_FIN/share:${GZ_SIM_RESOURCE_PATH}"

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
export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:$HOME/Industrial_Robotics/install/URDF_FIN/share:${GZ_SIM_RESOURCE_PATH}"
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
│   ├── tinker_robot/
│   └── tinker_moveit_config/
│       ├── config/
│       │   ├── URDF_FIN.srdf
│       │   ├── joint_limits.yaml
│       │   └── moveit_controllers.yaml
│       └── launch/
│           └── terminal7.launch.py
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


---

## TINKER_ARM — Seven-terminal launch (six existing processes + MoveIt 2)

This setup **retains the original six-terminal commands exactly as documented above** and adds MoveIt 2 as **Terminal 7**. Start each terminal in order, with Gazebo's controllers active before moving the arm.

| Terminal | Component | Purpose |
| --- | --- | --- |
| 1 | Gazebo Harmonic | Robot simulation and ROS 2 controllers |
| 2 | Original RViz | Visualization of Gazebo feedback |
| 3 | `joint_command_subscriber` | Central hub for the three manual command interfaces |
| 4 | Original ROS joint sliders | Radians |
| 5 | Interactive terminal controller | Degrees |
| 6 | Tkinter joint GUI | Degrees |
| **7** | **MoveIt 2 and MoveIt RViz** | **Planning and trajectory execution** |

### Before starting

The MoveIt configuration package `tinker_moveit_config` and its permanent [Terminal 7 launcher](src/tinker_moveit_config/launch/terminal7.launch.py) are included in this repository. Install MoveIt 2 for Jazzy using the installation instructions above, then build and source the workspace.

The committed [controller YAML](src/URDF_FIN/config/URDF_FIN_controllers.yaml) already enables `allow_partial_joints_goal: true` under `joint_trajectory_controller.ros__parameters`. This lets the shared seven-joint controller accept arm-only and gripper-only trajectories. No manual YAML modification or temporary launch file is required.

### Terminal 1 — Gazebo

~~~bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export GZ_SIM_RESOURCE_PATH="$HOME/Industrial_Robotics/src:$HOME/Industrial_Robotics/install/URDF_FIN/share:${GZ_SIM_RESOURCE_PATH}"
ros2 launch URDF_FIN gazebo.launch.py
~~~

### Terminal 2 — Original RViz

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run rviz2 rviz2 \
  -d ~/Industrial_Robotics/src/URDF_FIN/config/urdf.rviz \
  --ros-args -p use_sim_time:=true
~~~

### Terminal 3 — Synchronization hub

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot joint_command_subscriber
~~~

Wait for `READY: all seven controller joints detected; synchronized modes enabled.`

### Terminal 4 — Original joint sliders

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run joint_state_publisher_gui \
  joint_state_publisher_gui \
  --ros-args \
  -r /joint_states:=/slider_joint_states \
  -p source_list:="['/tinker/joint_sync']"
~~~

### Terminal 5 — Terminal controller

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot controller_publisher
~~~

Example: `Joint_3 25`, then `show`.

### Terminal 6 — Tkinter GUI

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 run tinker_robot joint_gui_controller
~~~

### Terminal 7 — MoveIt 2 + MoveIt RViz (one terminal)

Run these commands in Terminal 7 after Gazebo's controllers are active.

~~~bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch tinker_moveit_config terminal7.launch.py
~~~

The original RViz (Terminal 2) and MoveIt RViz (Terminal 7) open as separate windows. The permanent launch file is installed by the MoveIt package and survives WSL restarts. No temporary file is needed.

If the package cannot be found, rebuild it and source the workspace again:

~~~bash
cd ~/Industrial_Robotics
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select URDF_FIN tinker_moveit_config
source install/setup.bash
~~~

### Verify and use the system

In a spare terminal, source Jazzy and the workspace, then check:

~~~bash
source /opt/ros/jazzy/setup.bash
source ~/Industrial_Robotics/install/setup.bash
ros2 control list_controllers
ros2 param get /joint_trajectory_controller allow_partial_joints_goal
ros2 param get /move_group use_sim_time
ros2 topic echo /clock --once
ros2 action info /move_action
ros2 action info /execute_trajectory
ros2 action info /joint_trajectory_controller/follow_joint_trajectory
ros2 topic echo /joint_states --once
~~~

Both controllers should be `active`. Both parameter checks should return `True`, `/clock` should publish Gazebo simulation time, and each action should have exactly one action server.

In **MoveIt RViz**, select the `arm_group` planning group, use Start State `<current>`, choose a different valid goal (for example `zero_pose` or `JOE_POSE`), and press **Plan & Execute**. This computes a fresh trajectory from the latest robot state instead of executing an old stored plan.

### Synchronization and command-conflict warning

The **original three manual interfaces** remain synchronized through the existing hub. MoveIt receives robot-position feedback from Gazebo's `/joint_states` and can plan from the actual robot state after a manual movement.

**MoveIt is not yet fully integrated into the hub's shared target state:** its `FollowJointTrajectory` action sends goals directly to the Gazebo trajectory controller, while the original hub uses the controller's trajectory command topic. Gazebo and RViz (and the GUI's **actual position** labels) can reflect MoveIt-driven movement, but the hub's stored **target positions** and original sliders are **not guaranteed to update to MoveIt's new targets** without further code changes.

**Do not operate manual controls while MoveIt is executing**, because concurrent topic commands can interfere with an action trajectory. Do not run the legacy `slider_bridge.py`, `display.launch.py`, or duplicate controller managers alongside these seven terminals.


---

## MoveIt 2 — Add or edit saved robot poses

Use **MoveIt Setup Assistant** to create named poses such as `pose_3`, `home`, or `gripper_open`. **The Setup Assistant edits the MoveIt configuration; Terminal 7 runs the resulting poses** in MoveIt RViz. The original six-terminal commands do not change.

### 1. Open MoveIt Setup Assistant in a separate terminal

For editing, stop MoveIt and its RViz window first (Terminal 7 in the full system, or Terminal 2 in the two-terminal mode). Keep Gazebo running if desired and leave manual controls idle. Then:

~~~bash
cd ~/Industrial_Robotics

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch moveit_setup_assistant setup_assistant.launch.py
~~~

### 2. Load your **existing** MoveIt configuration

1. Choose **Edit Existing MoveIt Configuration Package**, **not** Create New.
2. Select `~/Industrial_Robotics/src/tinker_moveit_config`.
3. Wait for the robot and its existing planning groups and poses to load.

### 3. Create the pose

1. In the left sidebar, choose **Robot Poses**.
2. Click **Add Pose**.
3. Choose the planning group: `arm_group` for the five arm joints or `hand_group` for the two gripper joints.
4. Enter a unique name (for example, `pose_3`).
5. Adjust the joint sliders to the desired joint angles within the robot's limits.
6. Save the pose, and repeat for additional named poses.

Named robot poses are stored in the MoveIt configuration's SRDF (for this robot, `src/tinker_moveit_config/config/URDF_FIN.srdf`).

### 4. Back up the working package, then generate **only the SRDF**

**Clicking Save in Robot Poses does not necessarily write the updated poses to the installed MoveIt configuration.** The tested procedure is to regenerate the SRDF through **Configuration Files**.

Before generating, back up the existing MoveIt package **outside the workspace** so colcon does not detect a second ROS package:

~~~bash
mkdir -p ~/Industrial_Robotics_backups
cp -a ~/Industrial_Robotics/src/tinker_moveit_config \
      ~/Industrial_Robotics_backups/tinker_moveit_config_$(date +%Y%m%d_%H%M%S)
~~~

In the **MoveIt Setup Assistant**:

1. Check that the new named pose appears under **Robot Poses** and click **Save**.
2. Click **Configuration Files** in the left sidebar.
3. Keep the existing output directory: `~/Industrial_Robotics/src/tinker_moveit_config`.
4. If a **Files Modified** warning appears, acknowledge it and inspect the generation checklist.
5. **Uncheck every generated file except `config/URDF_FIN.srdf`.**
6. Confirm `config/moveit_controllers.yaml`, `config/joint_limits.yaml`, and all `launch/*.launch.py` files are **unchecked**.
7. Click **Generate Package**, then exit Setup Assistant.

**Why only SRDF?** Named poses are stored in `config/URDF_FIN.srdf`. Keeping the other files unchecked preserves the working MoveIt controllers, joint limits, Gazebo compatibility, and seven-terminal launches.

### Fix verified for `hand_group` — left joint must be negative

After adding poses, the `close_hand` plan failed with OMPL's `Insufficient states in sampleable goal region`. The SRDF had mistakenly saved `Left_Joint` as **`+0.06` rad** (outside the robot's joint range of `-0.78` to `0` rad). The correction that restored planning was:

~~~xml
<group_state name="close_hand" group="hand_group">
    <joint name="Left_Joint" value="-0.06"/>
    <joint name="Right_Joint" value="0.06"/>
</group_state>
~~~

The two fingers have opposite joint signs: **left negative, right positive**. Keep saved gripper poses within their URDF limits. If the Setup Assistant regenerated an incorrect sign, carefully edit **only** the `close_hand` group state in `src/tinker_moveit_config/config/URDF_FIN.srdf` and preserve the remaining SRDF.

Verify the saved arm and hand poses before rebuilding:

~~~bash
cd ~/Industrial_Robotics
grep -n 'group_state' src/tinker_moveit_config/config/URDF_FIN.srdf
grep -A 3 'group_state name="close_hand"' \
  src/tinker_moveit_config/config/URDF_FIN.srdf
~~~

### 5. Rebuild and launch Terminal 7 again

Close Setup Assistant, then:

~~~bash
cd ~/Industrial_Robotics

source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select tinker_moveit_config
source install/setup.bash

ros2 launch tinker_moveit_config terminal7.launch.py
~~~

This uses the same permanent launcher in both the two-terminal and seven-terminal modes.

### 6. Select and execute the new pose in MoveIt RViz

1. Open the **MotionPlanning** panel.
2. Select the group you used when saving the pose (`arm_group` or `hand_group`).
3. Set **Start State** to `<current>`.
4. Select the newly saved pose (such as `pose_3`) under **Goal State**.
5. Choose **Plan & Execute** to plan from the latest actual Gazebo joint positions and execute the motion.

> **Safety and compatibility:** Edit named poses in Setup Assistant; do not use the ordinary MoveIt RViz window to permanently save new poses. Avoid regenerating the tested controller/launch configuration unnecessarily. Keep other manual control inputs idle while MoveIt executes.


## MoveIt troubleshooting

- **Duplicate action servers or stale simulation state:** Stop all ROS processes before launching a new session. In WSL, save work first, then run `wsl --shutdown` in Windows PowerShell (this terminates all running WSL distributions). Start with the two-terminal mode and verify the controllers and joint states before launching MoveIt.
- **Start state outside joint bounds:** Check `ros2 topic echo /joint_states --once`. The URDF limits for Joint_3 are −1.3 to +1.3 rad, and Joint_4 is limited to −π/2 to +π/2 rad (180° total). Avoid exact hard stops; the manual control hub applies additional conservative margins. If the simulation is stuck at an old limit, restart Gazebo before further planning.
- **Start state in collision or invalid gripper goal:** Inspect the collision report. Left_Joint is limited to −0.78 to 0 rad and Right_Joint to 0 to +0.78 rad. Do not disable collision checking just to make a plan succeed. Inspect the actual state and use a verified collision-free pose.
- **Planning succeeds but execution fails:** Check the controller action server, simulation time and actual joint feedback. Stop competing manual command publishers and test in the two-terminal mode. Do not launch duplicate MoveIt instances.

These workflows are intended for simulation; disconnect physical hardware during troubleshooting.
