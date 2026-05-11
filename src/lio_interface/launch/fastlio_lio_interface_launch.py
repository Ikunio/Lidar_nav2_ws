import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # config = os.path.join(
    #     get_package_share_directory('lio_interface'), 'config', 'static_tf.yaml')

    lio_interface_node = Node(
        package='lio_interface',
        executable='lio_interface_node',
        namespace='',
        output='screen',
        emulate_tty=True,  # 开启提示颜色
        parameters=[{
            'use_sim_time': True,
            'odometry_sub': '/Odometry',
        }],
    )

    return LaunchDescription([lio_interface_node])
