from setuptools import find_packages, setup

package_name = 'tinker_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joe',
    maintainer_email='youssefhanyeng@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		        'joint_monitor = tinker_robot.joint_monitor:main',
                'controller_publisher = tinker_robot.controller_publisher:main',
                'joint_command_subscriber = tinker_robot.joint_command_subscriber:main',
                'joint_gui_controller = tinker_robot.joint_gui_controller:main',
        ],
    },
)
