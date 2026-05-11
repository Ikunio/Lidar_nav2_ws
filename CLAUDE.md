# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

ROS 2 Humble 工作空间，用于 3D LiDAR 自主导航（GLD 机器人团队）。

## 构建

```bash
./build.sh
# 等价于: colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

每次修改代码后需重新构建。构建前需 `source install/setup.bash`。

## 项目架构

四轮滑移转向机器人 + Livox MID-360 3D LiDAR + IMU，支持 Gazebo 仿真和实机。

### 数据流

```
LiDAR/IMU
  → ign_sim_pointcloud_tool (仅仿真，转 Velodyne 格式，添加 ring/time 字段)
  → FAST-LIO 或 Point-LIO (3D 里程计)
  → lio_interface (TF 桥接: LIO 内部坐标系 → odom)
  → sensor_scan_generation (odom → base_footprint TF，发布 /odom 和 /registered_scan)
  → pointcloud_to_laserscan (3D → 2D /scan，切片高度 0.2-1.0m)
  → small_gicp_relocalization (map → odom TF，替代 AMCL)
  → Nav2 (DWB 局部规划 + Navfn 全局规划)
```

TF 坐标系: `map → odom → base_footprint → livox_frame`

### 功能包

| 包名 | 用途 |
|------|------|
| `get_urdf` | Gazebo 仿真机器人模型和启动 |
| `gld_robot_description` | 实机机器人 URDF |
| `livox_laser_simulation_RO2` | Livox LiDAR Gazebo 仿真插件 |
| `livox_ros_driver2` | Livox MID-360 实机驱动（SMBU 修改版） |
| `FAST_LIO` | FAST-LIO2 里程计（ikd-Tree） |
| `point_lio` | Point-LIO 里程计（iVox，默认 LIO） |
| `Sophus` | 李群库（LIO 依赖，纯 cmake 包） |
| `lio_interface` | LIO 里程计 → Nav2 TF 桥接 |
| `sensor_scan_generation` | 3D 点云处理，发布 odom TF 和 /odom |
| `ign_sim_pointcloud_tool` | 仿真点云格式转换（PointCloud2 → Velodyne 格式） |
| `pcd2pgm-master` | PCD 点云 → 2D 占用栅格地图（离线工具） |
| `small_gicp_relocalization` | 基于 small_gicp 的重定位（替代 AMCL） |
| `me_nav2_bringup` | Nav2 集成启动包（配置、地图、PCD） |
| `gui_teleop` | tkinter GUI 遥控 |

额外重定位方案: `global_small_gicp_relocalization`（多分辨率 GICP）、`global_relocalization`（早期原型）、`icp_registration`（PCL ICP 粗精两阶段）

## 常用操作

### 仿真建图
```bash
./mapping_sim.sh        # 启动 Gazebo + FAST-LIO + SLAM Toolbox
# 驾驶机器人遍历环境后:
./save_map.sh           # 保存 2D 地图
./save_pcd.sh           # 保存 3D 点云，移至 src/me_nav2_bringup/pcd/
```

### 仿真导航
1. 修改 `src/registration/small_gicp_relocalization/launch/small_gicp_relocalization_launch.py` 中 `prior_pcd_file` 指向 PCD 文件
2. 修改 `src/me_nav2_bringup/launch/my_nav2_launch.py` 中 `map_yaml_file` 指向地图
3. `./nav2_sim.sh`

### 实机建图/导航
同上，将脚本替换为 `./mapping_real.sh` / `./nav2_real.sh`

### 调试工具
```bash
./show_tf_tree.sh       # 生成 TF 树 (ros2 run tf2_tools view_frames)
```

## LIO 选择与配置

默认使用 Point-LIO，FAST-LIO 为备选。在启动脚本中通过注释切换。两者的关键区别：

| | FAST-LIO | Point-LIO |
|---|---|---|
| 仿真 LiDAR 驱动 | `xfer_format=0` (PointCloud2) | `xfer_format=1` (CustomMsg) |
| 实机 LiDAR 驱动 | `xfer_format=0` | `xfer_format=1` |
| 仿真 config | `mid360.yaml` (lidar_type=5) | `mid360_sim.yaml` (lidar_type=2) |
| 实机 config | `mid360.yaml` (lidar_type=4) | `mid360_real.yaml` (lidar_type=1) |
| lio_interface | `fastlio_lio_interface_launch.py` (订阅 `/Odometry`) | `pointlio_lio_interface_launch.py` (订阅 `/aft_mapped_to_init`) |
| 仿真需 ign_sim_pointcloud_tool | 否（直接处理 PointCloud2） | 是（需要 ring/time 字段） |

注意：lidar_type 枚举在 FAST-LIO 和 Point-LIO 中定义不同，不要混淆。

## 关键配置文件

- Nav2 参数: `src/me_nav2_bringup/config/nav2_params.yaml`
- SLAM 参数: `src/me_nav2_bringup/config/slam_toolbox_params.yaml`
- 3D→2D 转换参数: `src/me_nav2_bringup/config/Pointcloud2d_3d.yaml`
- FAST-LIO 配置: `src/localization/FAST_LIO/config/mid360.yaml`
- Point-LIO 配置: `src/localization/point_lio/config/mid360_sim.yaml` (仿真) / `mid360_real.yaml` (实机)
- LiDAR 网络配置: `src/livox_ros_driver2/config/MID360_config.json`
- ICP 配置: `src/registration/icp_registration/config/icp.yaml`
- 启动说明: `启动说明书.md`

## 开发约定

- C++ 包使用 `ament_cmake`，Python 包使用 `ament_python`
- 包格式: ROS 2 package format 3
- 实机部署需 Livox-SDK2（已预编译在 `livox_ros_driver2/3rdparty/` 中，支持 amd64/arm64）
- 仿真需要先 `killall -9 gzserver gzclient` 杀死残留 Gazebo 进程
- 无单元测试，仅有 `ament_lint_auto` 静态分析
- `small_gicp_relocalization` 有最完整的 lint 配置（clang-format, clang-tidy, black, xmllint, copyright）
