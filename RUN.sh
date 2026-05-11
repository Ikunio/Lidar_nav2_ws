#!/bin/bash

# gnome-terminal --title="map" -- bash -c "source install/setup.bash; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true"
# gnome-terminal --title="rviz2" -- bash -c "source install/setup.bash; rviz2"

# fast_lio
# ros2 launch fast_lio mapping.launch.py use_sim_time:=true

# 旧版导航
# gnome-terminal --title="nav2" -- bash -c "
# source install/setup.bash; 
# ros2 launch nav2_bringup bringup_launch.py \
# use_sim_time:=True \
# map:=/home/pio/Nav2_ws/src/nav2/maps/test_map.yaml \
# params_file:=/home/pio/Nav2_ws/src/nav2/config/my_nav2_params.yaml"

# 删除后台运行的Gazebo进程
# killall -9 gzserver gzclient

# 键盘控制
# ros2 run teleop_twist_keyboard teleop_twist_keyboard

# slam_toolbox 边建图边导航
# gnome-terminal --title="bringup" -- bash -c "source install/setup.bash; \
# ros2 launch nav2_bringup bringup_launch.py \
# use_sim_time:=True \
# slam:=True \
# map:=/home/pio/Nav2_ws/src/nav2/maps/test_map.yaml \
# params_file:=/home/pio/Nav2_ws/src/nav2/config/my_nav2_params.yaml"

# # slam_toolbox 纯定位
# gnome-terminal --title="localization" -- bash -c "source install/setup.bash; \
# ros2 launch slam_toolbox localization_launch.py \
# use_sim_time:=True \
# slam_params_file:=/home/pio/Nav2_ws/src/nav2/config/my_localization_params.yaml"

# # nav2 纯导航
# gnome-terminal --title="navigation" -- bash -c "source install/setup.bash; \
# ros2 launch nav2_bringup navigation_launch.py \
# use_sim_time:=True \
# params_file:=/home/pio/Nav2_ws/src/nav2/config/my_nav2_params.yaml"


# 3D SLAM

gnome-terminal --title="urdf" -- bash -c "
killall -9 gzserver gzclient;
source install/setup.bash; 
ros2 launch get_urdf get_urdf_launch.py"

# fast-lio 里程计
gnome-terminal --title="fast-lio 里程计" -- bash -c "
source install/setup.bash; 
ros2 launch fast_lio mapping.launch.py use_sim_time:=true"

gnome-terminal --title="lio_interface" -- bash -c "
source install/setup.bash; 
ros2 launch lio_interface lio_interface_launch.py"

gnome-terminal --title="sensor_scan_generation" -- bash -c "
source install/setup.bash;
ros2 launch sensor_scan_generation sensor_scan_generation_launch.py"

# 3d点云转2d点云
gnome-terminal --title="3d点云转2d点云" -- bash -c "
source install/setup.bash; 
ros2 launch me_nav2_bringup pointcloud_to_laserscan_launch.py"

# small_gicp_relocalization 位姿重定位
gnome-terminal --title="small_gicp_relocalization" -- bash -c "
source install/setup.bash; 
ros2 launch small_gicp_relocalization small_gicp_relocalization_launch.py"

# slam_toolbox 边建图边导航 (使用自定义参数文件，设置 min_laser_range: 0.45)

# ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true 

# ros2 launch slam_toolbox online_async_launch.py \
#     use_sim_time:=true \
#     slam_params_file:=/home/pio/Nav2_3D_ws/src/me_nav2_bringup/config/slam_toolbox_params.yaml