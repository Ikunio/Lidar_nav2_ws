# Nav2_3D

<div align="center">
**3D LiDAR 自主导航系统 — 基于 Livox MID-360 的导航工作空间**

[![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22313F?logo=ros)](https://docs.ros.org/en/humble/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)](https://releases.ubuntu.com/22.04/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Gazebo](https://img.shields.io/badge/Gazebo-Fortress-orange)](https://gazebosim.org/)




---

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
  - [仿真建图](#仿真建图)
  - [仿真导航](#仿真导航)
  - [实机建图](#实机建图)
  - [实机导航](#实机导航)
- [功能包](#功能包)
- [配置说明](#配置说明)
  - [关键配置文件](#关键配置文件)
  - [LIO 切换](#lio-切换)
- [关键话题](#关键话题)
- [常见问题](#常见问题)
- [致谢](#致谢)
- [许可证](#许可证)

---

## 概述

Nav2_3D 是一个面向四轮滑移转向机器人的 3D LiDAR 自主导航工作空间。系统以 Livox MID-360 3D LiDAR 为核心传感器，集成 LIO（LiDAR-Inertial Odometry）里程计和 Nav2 导航框架，支持 **Gazebo 仿真**和**实机部署**两种模式。

**核心特性：**

- **双 LIO 里程计** — 支持 FAST-LIO2 和 Point-LIO，可灵活切换
- **3D 重定位** — 基于 small_gicp / KISS-Matcher 的全局重定位
- **仿真-实机一致性** — 同一套导航栈，仅切换启动脚本和传感器驱动
- **完整工具链** — 建图 → 保存 → 导航全流程脚本化

---

## 快速开始

### 环境要求

- **操作系统**: Ubuntu 22.04
- **ROS 2**: Humble Hawksbill
- **Gazebo**: Fortress (仿真模式)
- **Livox-SDK2**: 实机模式需要（已预编译在 `src/livox_ros_driver2/3rdparty/`，支持 amd64/arm64）

### 构建

```bash
source /opt/ros/humble/setup.bash
./build.sh
# 等价于: colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

> **注意:** 每次修改源代码后需要重新构建。构建前确保已 `source install/setup.bash`。

### 5 分钟跑通仿真建图

```bash
# 1. 构建并 source
source install/setup.bash

# 2. 启动仿真建图
./mapping_sim.sh

# 在 GUI 遥控窗口用 WASD 驾驶机器人遍历环境，RViz 中可实时观察建图效果
```

### 仿真导航

```bash
# 1. 建图完成后保存数据
./save_map.sh       # 保存 2D 占用栅格地图 → src/me_nav2_bringup/map/
./save_pcd.sh       # 保存 3D 点云 → 手动移至 src/me_nav2_bringup/pcd/

# 2. 修改配置文件，指向新生成的地图和点云
#   - my_nav2_launch.py 中的 map_yaml_file
#   - small_gicp_relocalization_launch.py 中的 prior_pcd_file

# 3. 启动仿真导航
./nav2_sim.sh

# 4. 在 RViz 中使用 "2D Pose Estimate" 设置初始位姿，"Nav2 Goal" 发送目标点
```

---

## 使用指南

### 仿真建图

启动 8 个终端窗口，分别运行以下节点：

| 序号 | 功能包 | 作用 |
|:----:|--------|------|
| 1 | `gui_teleop` | GUI 键盘遥控（WASD 控制） |
| 2 | `FAST_LIO` | 3D LiDAR-IMU 里程计 |
| 3 | `lio_interface` | LIO 坐标系 → odom TF 桥接 |
| 4 | `get_urdf` | Gazebo 仿真 + robot_state_publisher + RViz |
| 5 | `sensor_scan_generation` | odom→base_footprint TF + `/odom` 发布 |
| 6 | `me_nav2_bringup` | 3D → 2D 激光扫描转换 |
| 7 | `slam_toolbox` | 在线异步建图 |
| 8 | `me_nav2_bringup` | Nav2 导航栈 |

```bash
source install/setup.bash
./mapping_sim.sh
```

### 仿真导航

启动 6 个终端窗口（无 SLAM Toolbox，使用预建地图 + ICP 重定位）：

| 序号 | 功能包 | 作用 |
|:----:|--------|------|
| 1 | `FAST_LIO` | 3D LiDAR-IMU 里程计 |
| 2 | `lio_interface` | 坐标系桥接 |
| 3 | `get_urdf` | Gazebo + robot_state_publisher + RViz |
| 4 | `sensor_scan_generation` | TF + `/odom` |
| 5 | `me_nav2_bringup` | 3D → 2D 转换 |
| 6 | `me_nav2_bringup` | Nav2 导航栈 |

```bash
./nav2_sim.sh
```

> small_gicp_relocalization 默认被注释。如需使用 ICP 重定位，取消 `nav2_sim.sh` 中相关行的注释并确保 PCD 文件路径正确。

### 实机建图

用实机 LiDAR 驱动和 URDF 替换仿真组件：

| 序号 | 功能包 | 作用 |
|:----:|--------|------|
| 1 | `livox_ros_driver2` | Livox MID-360 实机驱动 |
| 2 | `FAST_LIO` | 3D LiDAR-IMU 里程计 |
| 3 | `lio_interface` | 坐标系桥接 |
| 4 | `gld_robot_description` | 实机 URDF + RViz |
| 5 | `sensor_scan_generation` | TF + `/odom` |
| 6 | `me_nav2_bringup` | 3D → 2D 转换 |
| 7 | `slam_toolbox` | 在线建图 |

```bash
./mapping_real.sh
```

### 实机导航

| 序号 | 功能包 | 作用 |
|:----:|--------|------|
| 1 | `livox_ros_driver2` | 实机 LiDAR 驱动 |
| 2 | `FAST_LIO` | 3D 里程计 |
| 3 | `lio_interface` | 坐标系桥接 |
| 4 | `gld_robot_description` | 实机 URDF + RViz |
| 5 | `sensor_scan_generation` | TF + `/odom` |
| 6 | `me_nav2_bringup` | 3D → 2D 转换 |
| 7 | `small_gicp_relocalization` | ICP 重定位 |
| 8 | `me_nav2_bringup` | Nav2 导航栈 |

```bash
./nav2_real.sh
```

### 保存地图与点云

```bash
./save_map.sh       # 保存 2D 栅格地图 (PGM + YAML)
./save_pcd.sh       # 保存 3D 点云 (PCD)，手动移至 src/me_nav2_bringup/pcd/
```

### 调试工具

```bash
./show_tf_tree.sh   # 生成 TF 坐标树 PDF
```

---

## 功能包

### 仿真

| 包名 | 路径 | 说明 |
|------|------|------|
| `get_urdf` | `src/get_urdf/` | 四轮小车 URDF 模型、Gazebo 世界、RViz 配置 |
| `livox_laser_simulation_RO2` | `src/livox_laser_simulation_RO2/` | Livox LiDAR Gazebo 仿真插件 |
| `ign_sim_pointcloud_tool` | `src/ign_sim_pointcloud_tool/` | 点云格式转换（PointCloud2 → Velodyne 格式），Point-LIO 仿真必需 |

### 实机

| 包名 | 路径 | 说明 |
|------|------|------|
| `gld_robot_description` | `src/gld_robot_description/` | 实机 URDF 模型（含 RealSense D456/D405、Orbbec Gemini） |
| `livox_ros_driver2` | `src/livox_ros_driver2/` | Livox MID-360 驱动（SMBU 修改版），同时发布 CustomMsg 和 PointCloud2 |

### 里程计

| 包名 | 路径 | 说明 |
|------|------|------|
| `FAST_LIO` | `src/localization/FAST_LIO/` | FAST-LIO2：基于 ikd-Tree 的紧耦合 LiDAR-IMU 里程计，100Hz+ |
| `point_lio` | `src/localization/point_lio/` | Point-LIO：高带宽里程计（4-8kHz），抗 IMU 饱和和剧烈振动 |
| `Sophus` | `src/localization/Sophus/` | 李群库 (SO(3)/SE(3))，LIO 数学依赖 |

### 数据桥接

| 包名 | 路径 | 说明 |
|------|------|------|
| `lio_interface` | `src/lio_interface/` | LIO 内部坐标系 → 标准 odom 坐标系 TF 转换 |
| `sensor_scan_generation` | `src/sensor_scan_generation/` | 发布 odom→base_footprint TF 和 `/odom`，数值微分计算速度 |

### 地图工具

| 包名 | 路径 | 说明 |
|------|------|------|
| `pcd2pgm-master` | `src/pcd2pgm-master/` | PCD 点云 → 2D 占用栅格地图离线转换工具 |

### 重定位

| 包名 | 路径 | 说明 |
|------|------|------|
| `small_gicp_relocalization` | `src/registration/small_gicp_relocalization/` | **主要方案**：基于 small_gicp 的 3D 点云重定位，替代 AMCL |
| `global_small_gicp_relocalization` | `src/registration/global_small_gicp_relocalization/` | 多分辨率 GICP 全局重定位 |
| `global_relocalization_kiss_matcher` | `src/registration/global_relocalization_kiss_matcher/` | 基于 KISS-Matcher + GTSAM 的全局重定位 |
| `global_relocalization` | `src/registration/global_relocalization/` | 全局重定位早期原型 |
| `icp_registration` | `src/registration/icp_registration/` | PCL ICP 粗-精两阶段配准 |
| `KISS-Matcher` | `src/registration/KISS-Matcher/` | ICRA 2025：快速点云全局配准库 (FPFH + TEASER++ + small_gicp) |

### 导航

| 包名 | 路径 | 说明 |
|------|------|------|
| `me_nav2_bringup` | `src/me_nav2_bringup/` | Nav2 集成启动包：参数配置、地图、PCD、RViz |
| `gui_teleop` | `src/gui_teleop/` | tkinter GUI 遥控，WASD 控制，支持速度调节和紧急停止 |

---

## 配置说明

### 关键配置文件

| 文件 | 说明 |
|------|------|
| `src/me_nav2_bringup/config/nav2_params.yaml` | Nav2 完整参数（DWB 控制器 + Navfn 全局规划器） |
| `src/me_nav2_bringup/config/slam_toolbox_params.yaml` | SLAM Toolbox 在线建图参数 |
| `src/me_nav2_bringup/config/Pointcloud2d_3d.yaml` | 3D→2D 切片高度、角度分辨率参数 |
| `src/localization/FAST_LIO/config/mid360.yaml` | FAST-LIO 里程计参数 |
| `src/localization/point_lio/config/mid360_sim.yaml` | Point-LIO 仿真参数 |
| `src/localization/point_lio/config/mid360_real.yaml` | Point-LIO 实机参数 |
| `src/livox_ros_driver2/config/MID360_config.json` | LiDAR 网络配置（IP、数据格式） |
| `src/registration/icp_registration/config/icp.yaml` | ICP 配准参数 |

### Nav2 参数要点

当前配置使用 **DWB 局部规划器** + **Navfn 全局规划器** (Dijkstra)：

| 参数 | 值 | 说明 |
|------|-----|------|
| `max_vel_x` | 0.26 m/s | 最大线速度 |
| `max_vel_theta` | 1.0 rad/s | 最大角速度 |
| `xy_goal_tolerance` | 0.035 m | 目标位置容差 |
| `yaw_goal_tolerance` | 0.1745 rad (10°) | 目标朝向容差 |
| `local_costmap` | 6×6 m, 0.05 m/格 | 局部代价地图 |
| `global_costmap` | 静态 + 障碍物 + 膨胀层 | 全局代价地图 |
| `robot_footprint` | 0.42×0.39 m 矩形 | 机器人外轮廓 |

### LIO 切换

默认使用 **FAST-LIO**，可在启动脚本中注释/取消注释切换到 **Point-LIO**。

| 配置项 | FAST-LIO | Point-LIO |
|--------|----------|-----------|
| 仿真 LiDAR xfer_format | `0` (PointCloud2) | `1` (CustomMsg) |
| 实机 LiDAR xfer_format | `0` | `1` |
| 仿真配置文件 | `mid360.yaml` (lidar_type=5) | `mid360_sim.yaml` (lidar_type=2) |
| 实机配置文件 | `mid360.yaml` (lidar_type=4) | `mid360_real.yaml` (lidar_type=1) |
| lio_interface 启动文件 | `fastlio_lio_interface_launch.py` | `pointlio_lio_interface_launch.py` |
| 里程计话题 | `/Odometry` | `/aft_mapped_to_init` |
| 仿真需格式转换 | 否 | 是（需 `ign_sim_pointcloud_tool`） |
| 核心数据结构 | ikd-Tree | iVox |
| 输出频率 | 100 Hz+ | 4-8 kHz |

> **注意:** `lidar_type` 枚举值在 FAST-LIO 和 Point-LIO 中定义不同，不可混用。

### 仿真 vs 实机差异

| | 仿真 | 实机 |
|---|---|---|
| LiDAR 输入 | Gazebo ray sensor | livox_ros_driver2 |
| 机器人模型 | `get_urdf` (simple_car.urdf) | `gld_robot_description` |
| use_sim_time | LIO 管线 `true` / Nav2 `false` | `false` |
| 点云格式转换 | Point-LIO 需要 ign_sim_pointcloud_tool | 不需要 |

---

## 关键话题

| 话题 | 消息类型 | 发布者 | 说明 |
|------|----------|--------|------|
| `/livox/lidar` | `PointCloud2` / `CustomMsg` | LiDAR 驱动 | 原始点云 |
| `/livox/imu` | `sensor_msgs/Imu` | LiDAR 内置 IMU | IMU 数据 |
| `/cloud_registered` | `sensor_msgs/PointCloud2` | FAST-LIO / Point-LIO | 配准后点云 |
| `/Odometry` | `nav_msgs/Odometry` | FAST-LIO | LIO 里程计 |
| `/aft_mapped_to_init` | `nav_msgs/Odometry` | Point-LIO | LIO 里程计 |
| `/registered_scan` | `sensor_msgs/PointCloud2` | sensor_scan_generation | odom 系点云 |
| `/registered_odometry` | `nav_msgs/Odometry` | sensor_scan_generation | odom 系里程计 |
| `/odom` | `nav_msgs/Odometry` | sensor_scan_generation | Nav2 使用的里程计 |
| `/scan` | `sensor_msgs/LaserScan` | pointcloud_to_laserscan | 2D 激光扫描 |
| `/cmd_vel` | `geometry_msgs/Twist` | Nav2 | 速度指令 |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | RViz | 初始位姿估计 |
| `/tf` | `tf2_msgs/TFMessage` | 多个节点 | 坐标变换 |

---

## 常见问题

### Gazebo 无法启动

残留的 Gazebo 进程会阻止新实例启动。启动脚本默认会先执行 `killall -9 gzserver gzclient`。若仍失败，手动运行：

```bash
killall -9 gzserver gzclient
```

### LIO 里程计不收敛 / 机器人乱飞

1. 检查 IMU 话题是否有数据：`ros2 topic echo /livox/imu`
2. 检查 LiDAR 话题是否有数据：`ros2 topic echo /livox/lidar`
3. 确认 `lidar_type` 配置与实际传感器类型匹配
4. 仿真模式下确认 `use_sim_time` 设置正确

### TF 断开 / Nav2 代价地图空白

1. 检查 TF 树完整性：`./show_tf_tree.sh`
2. 确认所有终端窗口均已正常启动且无报错
3. 检查 `/scan` 话题是否有数据：`ros2 topic echo /scan`
4. 确认 `pointcloud_to_laserscan` 的 `target_frame` 与 LiDAR 坐标系一致

### 重定位不成功

1. 确认 PCD 文件路径正确且文件存在
2. 确认 PCD 是建图时保存的完整点云（非空文件）
3. 在 RViz 中使用 "2D Pose Estimate" 给出大致初始位姿
4. 尝试使用 `global_small_gicp_relocalization` 或 `global_relocalization_kiss_matcher` 进行全局重定位

### 实机 LiDAR 无数据

1. 检查网线连接，确认 LiDAR IP 配置（默认 192.168.1.1xx）
2. 检查 `MID360_config.json` 中的 IP 地址和端口
3. 确认 `Livox-SDK2` 已正确安装

### 构建失败

```bash
# 清理构建产物后重试
rm -rf build/ install/ log/
./build.sh
```

---

## 致谢

本项目基于以下优秀的开源项目构建：

| 项目 | 说明 | 许可证 |
|------|------|--------|
| [FAST-LIO2](https://github.com/hku-mars/FAST_LIO) | 紧耦合 LiDAR-IMU 里程计 | BSD |
| [Point-LIO](https://github.com/hku-mars/Point-LIO) | 高带宽 LiDAR-IMU 里程计 | BSD |
| [Nav2](https://github.com/ros-planning/navigation2) | ROS 2 导航框架 | Apache 2.0 |
| [small_gicp](https://github.com/koide3/small_gicp) | 高效 GICP 点云配准 | MIT |
| [KISS-Matcher](https://github.com/MIT-SPARK/KISS-Matcher) | 快速全局点云配准 (ICRA 2025) | MIT |
| [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox) | 2D SLAM | LGPL 2.1 |
| [Livox SDK2](https://github.com/Livox-SDK/Livox-SDK2) | Livox LiDAR SDK | MIT |
| [Sophus](https://github.com/strasdat/Sophus) | 李群 C++ 库 | MIT |

---

## 许可证

本项目依据 [MIT License](./LICENSE) 开源。

---

<div align="center">

**GLD 机器人团队** · [Issues](https://github.com/ikunio/Nav2-3D/issues) · [Pull Requests](https://github.com/ikunio/Nav2-3D/pulls)

</div>
