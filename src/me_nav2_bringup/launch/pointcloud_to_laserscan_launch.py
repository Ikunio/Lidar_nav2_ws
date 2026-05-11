import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    config_file = os.path.join(
        get_package_share_directory('me_nav2_bringup'),
        'config',
        'Pointcloud2d_3d.yaml'
    )

    # 定义 pointcloud_to_laserscan 节点
    pc2l_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='Pointcloud2d_3d',  
        output='screen',
        parameters=[config_file],
        remappings=[
            ('cloud_in', '/registered_scan'),   # 输入3d点云
            ('scan', '/scan')               # 输出2d点云
        ]
    )

    return LaunchDescription([
        pc2l_node
    ])