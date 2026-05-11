import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 获取共享目录路径
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    me_share_path = get_package_share_directory('me_nav2_bringup')

    # 配置文件与地图路径
    params_file = os.path.join(me_share_path, 'config', 'nav2_params.yaml')
    map_yaml_file = os.path.join(me_share_path, 'map', 'nav_test_4_27.yaml')
    rviz_file = os.path.join(me_share_path, 'rviz', 'nav2.rviz')
    
    # 是否使用仿真时间
    use_sim_time = False # False 

    # 启动纯导航组件，不使用AMCL
    navigation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': str(use_sim_time),
            'autostart': 'True'
        }.items()
    )

    # 独立启动 Map Server
    # 加载静态地图，供 Global Costmap 使用
    map_server_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        # 同时传入你的 nav2_params.yaml 和 地图文件路径
        parameters=[params_file, {'yaml_filename': map_yaml_file, 'use_sim_time': use_sim_time}]
    )

    # 启动 Map Server 的生命周期管理器
    # 负责将 map_server 从 Unconfigured 状态推送到 Active 状态
    lifecycle_manager_map_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': True},
            {'node_names': ['map_server']}
        ]
    )

    # rviz
    rviz_cmd = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_file], 
    )

    # 组合 LaunchDescription 返回
    ld = LaunchDescription()
    ld.add_action(navigation_cmd)
    ld.add_action(map_server_cmd)
    ld.add_action(lifecycle_manager_map_cmd)
    ld.add_action(rviz_cmd)

    return ld