#!/bin/bash

# 仿真建图启动脚本

# 杀死之前的 Gazebo 进程
# killall -9 gzserver gzclient

# 键盘控制
# ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 可能会导致 /cmd_vel 话题被占用
# gui控制小车
gnome-terminal --title="GUI控制" -- bash -c "
source install/setup.bash;
ros2 run gui_teleop gui_teleop_node"

# -----------------------------------------------------------------------------------
# 使用fast-lio作为里程计
gnome-terminal --title="FAST-LIO 里程计" -- bash -c "
source install/setup.bash;
ros2 launch fast_lio mapping.launch.py"

# 里程计接口
gnome-terminal --title="lio_interface" -- bash -c "
source install/setup.bash;
ros2 launch lio_interface lio_interface_launch.py"

# ------------------------------------------------------------------------------------

# 使用point-lio作为里程计
# gnome-terminal --title="点云格式转换器" -- bash -c "
# source install/setup.bash;
# ros2 run ign_sim_pointcloud_tool ign_sim_pointcloud_tool_node --ros-args \
#   -p pcd_topic:=/livox/lidar \
#   -p n_scan:=50 \
#   -p horizon_scan:=360 \
#   -p ang_bottom:=7.22 \
#   -p ang_res_y:=1.248"

# gnome-terminal --title="Point-LIO 里程计" -- bash -c "
# source install/setup.bash;
# ros2 launch point_lio point_lio.launch.py \
#   point_lio_cfg_dir:=/home/pio/Nav2_3D_ws/src/localization/point_lio/config/mid360_sim.yaml"

# gnome-terminal --title="lio_interface" -- bash -c "
# source install/setup.bash;
# ros2 launch lio_interface pointlio_lio_interface_launch.py"

# ------------------------------------------------------------------------------------

# Gazebo 仿真环境
gnome-terminal --title="Gazebo 仿真" -- bash -c "
killall -9 gzserver gzclient;
source install/setup.bash;
ros2 launch get_urdf get_urdf_launch.py"

gnome-terminal --title="sensor_scan_generation" -- bash -c "
source install/setup.bash;
ros2 launch sensor_scan_generation sensor_scan_generation_launch.py"

gnome-terminal --title="3d点云转2d" -- bash -c "
source install/setup.bash;
ros2 launch me_nav2_bringup pointcloud_to_laserscan_launch.py"

# gnome-terminal --title="slam_toolbox 建图" -- bash -c "
# source install/setup.bash;
# ros2 launch slam_toolbox online_async_launch.py"

gnome-terminal --title="slam_toolbox 建图" -- bash -c "
source install/setup.bash;
ros2 launch slam_toolbox online_async_launch.py \
    slam_params_file:=/home/pio/Nav2_3D_ws/src/me_nav2_bringup/config/slam_toolbox_params.yaml"

gnome-terminal --title="Nav2 导航" -- bash -c "
source install/setup.bash;
ros2 launch me_nav2_bringup my_nav2_launch.py"