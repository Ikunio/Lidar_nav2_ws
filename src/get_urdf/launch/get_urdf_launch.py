import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():


    # 动态获取 get_urdf 包在 install 目录下的绝对路径
    pkg_share_path = get_package_share_directory('get_urdf')

    rviz_config_path = os.path.join(pkg_share_path, 'rviz', 'nav2_new.rviz')

    world_file_path = os.path.join(pkg_share_path, 'worlds', 'test_world.world')

    # 拼接出准确的 URDF 路径
    urdf_file_path = os.path.join(pkg_share_path, 'model', 'simple_car.urdf')
    
    # 2. 读取 URDF 文件内容
    with open(urdf_file_path, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # 3. 启动 Gazebo 仿真引擎
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_file_path],
            output='screen'),

        # 4. 调用官方的 robot_state_publisher 节点
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            # 这里的键名必须是 'robot_description'
            parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]),

        # 5. 在 Gazebo 中生成机器人，数据源指向 robot_description 话题
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='urdf_spawner',
            output='screen',
            arguments=['-entity', 'simple_car', '-topic', 'robot_description']),

        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config_path], 
        )
        

    ])