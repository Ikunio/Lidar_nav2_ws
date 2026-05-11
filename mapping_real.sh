#!/bin/bash

# 实机建图启动脚本

# point_lio
# gnome-terminal --title="Livox Point-LIO 驱动" -- bash -c "
# source install/setup.bash;
# ros2 launch livox_ros_driver2 point_lio_msg_MID360_launch.py"

# gnome-terminal --title="Point-LIO 里程计" -- bash -c "
# source install/setup.bash;
# ros2 launch point_lio point_lio.launch.py \
#   point_lio_cfg_dir:=/home/pio/Nav2_3D_ws/src/localization/point_lio/config/mid360_real.yaml"

# gnome-terminal --title="Point-LIO lio_interface" -- bash -c "
# source install/setup.bash;
# ros2 launch lio_interface pointlio_lio_interface_launch.py"


# fast_lio
gnome-terminal --title="Livox Fast-LIO 驱动" -- bash -c "
source install/setup.bash;
ros2 launch livox_ros_driver2 fast_lio_msg_MID360_launch.py"

gnome-terminal --title="FAST-LIO 里程计" -- bash -c "
source install/setup.bash;
ros2 launch fast_lio mapping.launch.py"

gnome-terminal --title="Fast-LIO lio_interface" -- bash -c "
source install/setup.bash;
ros2 launch lio_interface fastlio_lio_interface_launch.py"

# ---------


gnome-terminal --title="机器人描述" -- bash -c "
killall -9 gzserver gzclient;
source install/setup.bash;
ros2 launch gld_robot_description gld_robot_description_launch.py"

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