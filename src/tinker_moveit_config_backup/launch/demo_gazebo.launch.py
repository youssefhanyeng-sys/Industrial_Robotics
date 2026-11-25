
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter


def include_launch(package_name, launch_filename):
    launch_path = os.path.join(
        get_package_share_directory(package_name),
        'launch',
        launch_filename
    )

    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_path)
    )


def generate_launch_description():

    # 1. Gazebo robot with its existing controllers
    gazebo = include_launch(
        'URDF_FIN',
        'gazebo.launch.py'
    )

    # 2. MoveIt2 motion-planning server
    move_group = include_launch(
        'tinker_moveit_config',
        'move_group.launch.py'
    )

    # 3. RViz with the MoveIt MotionPlanning plugin
    moveit_rviz = include_launch(
        'tinker_moveit_config',
        'moveit_rviz.launch.py'
    )

    return LaunchDescription([
        SetParameter(
            name='use_sim_time',
            value=True
        ),

        gazebo,
        move_group,
        moveit_rviz,
    ])
