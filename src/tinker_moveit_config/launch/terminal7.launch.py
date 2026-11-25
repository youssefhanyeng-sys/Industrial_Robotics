import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('tinker_moveit_config')

    move_group = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'move_group.launch.py')
        )
    )

    moveit_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'moveit_rviz.launch.py')
        )
    )

    return LaunchDescription([
        SetParameter(name='use_sim_time', value=True),

        SetParameter(
            name='trajectory_execution.allowed_execution_duration_scaling',
            value=2.0
        ),

        SetParameter(
            name='trajectory_execution.allowed_goal_duration_margin',
            value=5.0
        ),

        SetParameter(
            name='trajectory_execution.execution_duration_monitoring',
            value=True
        ),

        move_group,
        moveit_rviz
    ])
