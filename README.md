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
