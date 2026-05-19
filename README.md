# Lidar_nav2_ws

基于 ROS 2 的 3D LiDAR 自主导航系统

[![ROS2](https://img.shields.io/badge/ROS2-Humble-22313F?logo=ros)](https://docs.ros.org/en/humble/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu)](https://releases.ubuntu.com/22.04/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

**Nav2_3D** 是一个面向四轮滑移转向机器人的 ROS 2 Humble 导航工作空间。系统以 Livox MID-360 3D LiDAR 和 IMU 为核心传感器，集成 LiDAR-Inertial Odometry (LIO) 里程计、3D 点云重定位和 Nav2 导航框架，支持 **Gazebo 仿真**与**实机部署**，仅需切换启动脚本即可在两种模式间无缝切换。

核心特性：

- **双 LIO 后端** — FAST-LIO2 与 Point-LIO 可灵活切换
- **3D 重定位** — 基于 small_gicp / KISS-Matcher 的全局重定位
- **仿真-实机一致性** — 同一套导航栈，仅传感器驱动和 URDF 不同
- **完整工具链** — 构建、建图、保存地图、导航全流程脚本化

数据管线：

> LiDAR/IMU &rarr; LIO (FAST-LIO 或 Point-LIO) &rarr; TF 桥接 (`lio_interface`) &rarr; odom TF &amp; `/registered_scan` (`sensor_scan_generation`) &rarr; 3D&rarr;2D 切片 (`pointcloud_to_laserscan`) &rarr; 重定位 (`small_gicp_relocalization`) &rarr; Nav2 (DWB + Navfn)

TF 坐标树：**`map` &rarr; `odom` &rarr; `base_footprint` &rarr; `chassis` &rarr; `livox_frame`**

---

## 1. 环境要求

- **操作系统**：Ubuntu 22.04
- **ROS 2**：Humble Hawksbill
- **Gazebo**：Fortress
- **Livox-SDK2**：实机模式需要；已预编译于 `src/livox_ros_driver2/3rdparty/`，支持 amd64/arm64

## 2. 构建

```bash
source /opt/ros/humble/setup.bash
./build.sh
```

构建脚本等价于：

```bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

每次修改源代码后需重新构建。启动任何节点前确保已执行 `source install/setup.bash`。

## 3. 快速开始

### 3.1 仿真建图

```bash
source install/setup.bash
./mapping_sim.sh
```

此命令启动 Gazebo、FAST-LIO、SLAM Toolbox、Nav2 和 GUI 遥控窗口。使用 WASD 键驾驶机器人遍历环境。覆盖足够面积后保存地图：

```bash
./save_map.sh       # 保存 2D 占用栅格地图至 src/me_nav2_bringup/map/
./save_pcd.sh       # 保存 3D 点云，手动移至 src/me_nav2_bringup/pcd/
```

### 3.2 仿真导航

修改以下文件，指向新保存的地图和点云：

- `src/me_nav2_bringup/launch/my_nav2_launch.py` — 设置 `map_yaml_file`
- `src/registration/small_gicp_relocalization/launch/small_gicp_relocalization_launch.py` — 设置 `prior_pcd_file`

然后启动：

```bash
./nav2_sim.sh
```

在 RViz 中使用 **"Nav2 Goal"** 发送导航目标。

### 3.3 实机建图

```bash
./mapping_real.sh
```

将 Gazebo 替换为 Livox MID-360 硬件驱动 (`livox_ros_driver2`) 和实机 URDF (`gld_robot_description`)。

### 3.4 实机导航

```bash
./nav2_real.sh
```

包含 `small_gicp_relocalization`，基于先验 PCD 地图进行重定位。

## 4. 功能包

工作空间包含 **19 个 ROS 2 功能包**，位于 `src/` 下：

**里程计与定位** (`src/localization/`)

- `FAST_LIO` — FAST-LIO2：基于 ikd-Tree 的紧耦合 LiDAR-IMU 里程计，100 Hz+
- `point_lio` — Point-LIO：高带宽里程计 (4&ndash;8 kHz)，抗 IMU 饱和
- `Sophus` — 李群库 (SO(3)/SE(3))，LIO 数学依赖

**配准与重定位** (`src/registration/`)

- `small_gicp_relocalization` — 主重定位方案：基于 small_gicp 的 3D 点云配准
- `global_relocalization_kiss_matcher` — KISS-Matcher + GTSAM 全局重定位（粗配准+精配准）
- `KISS-Matcher` — ICRA 2025：快速全局点云配准 (FPFH + TEASER++ + small_gicp)

**传感器与桥接**

- `livox_ros_driver2` — Livox MID-360 驱动，同时发布 CustomMsg 和 PointCloud2
- `lio_interface` — TF 桥接：LIO 内部坐标系转标准 `odom` 坐标系
- `sensor_scan_generation` — 发布 `odom` &rarr; `base_footprint` TF、`/odom` 和 `/registered_scan`
- `ign_sim_pointcloud_tool` — PointCloud2 转 Velodyne 格式，Point-LIO 仿真必需

**导航**

- `me_nav2_bringup` — Nav2 集成：启动文件、参数配置、地图、PCD、RViz 配置
- `gui_teleop` — tkinter GUI 遥控，持速度调节和紧急停止

**仿真与描述**

- `get_urdf` — 四轮滑移转向机器人 URDF、Gazebo 世界、RViz 配置
- `gld_robot_description` — 实机 URDF（含 RealSense D456/D405、Orbbec Gemini 相机）
- `livox_laser_simulation_RO2` — Livox LiDAR Gazebo 仿真插件

**工具**

- `pcd2pgm-master` — PCD 点云转 2D 占用栅格地图离线工具

## 5. 配置说明

### 5.1 关键配置文件

| 文件 | 说明 |
|------|------|
| `src/me_nav2_bringup/config/nav2_params.yaml` | Nav2 参数 |
| `src/me_nav2_bringup/config/slam_toolbox_params.yaml` | SLAM Toolbox 在线建图参数 |
| `src/me_nav2_bringup/config/Pointcloud2d_3d.yaml` | 3D&rarr;2D 切片高度和角分辨率 |
| `src/localization/FAST_LIO/config/mid360.yaml` | FAST-LIO 参数 |
| `src/localization/point_lio/config/mid360_sim.yaml` | Point-LIO 仿真参数 |
| `src/localization/point_lio/config/mid360_real.yaml` | Point-LIO 实机参数 |
| `src/livox_ros_driver2/config/MID360_config.json` | LiDAR 网络配置 |
| `src/registration/icp_registration/config/icp.yaml` | ICP 配准参数 |

### 5.2 Nav2 参数要点

当前配置使用 **DWB** 局部规划器和 **Navfn**（Dijkstra）全局规划器。

- **速度限制**：线速度 0.26 m/s，角速度 1.0 rad/s
- **目标容差**：XY 0.035 m，偏航角 10&deg;
- **局部代价地图**：6&times;6 m 滚动窗口，0.05 m 分辨率
- **全局代价地图**：静态层 + 障碍物层 + 膨胀层（0.55 m 半径）
- **机器人外轮廓**：0.42&times;0.39 m 矩形

### 5.3 LIO 切换

默认使用 FAST-LIO。切换至 Point-LIO 需在启动脚本中注释/取消注释对应行。主要差异：

- **LiDAR 数据格式**：FAST-LIO 使用 `xfer_format=0`（PointCloud2）；Point-LIO 使用 `xfer_format=1`（CustomMsg）
- **配置文件**：`mid360.yaml`（FAST-LIO）vs. `mid360_sim.yaml` / `mid360_real.yaml`（Point-LIO）
- **lio_interface**：`fastlio_lio_interface_launch.py` 订阅 `/Odometry`；`pointlio_lio_interface_launch.py` 订阅 `/aft_mapped_to_init`
- **仿真**：Point-LIO 需要 `ign_sim_pointcloud_tool` 注入 ring/time 字段

> **注意**：`lidar_type` 枚举值在 FAST-LIO 和 Point-LIO 中定义不同，不可混用。

### 5.4 仿真与实机差异

仿真模式将 Livox 硬件驱动替换为 Gazebo 射线传感器插件，使用 `get_urdf` 替代 `gld_robot_description`。LIO 管线在仿真中使用 `use_sim_time=true`；Nav2 始终使用 `false`。

## 6. ROS 2 话题

| 话题 | 消息类型 | 发布者 |
|------|----------|--------|
| `/livox/lidar` | PointCloud2 / CustomMsg | LiDAR 驱动 |
| `/livox/imu` | sensor_msgs/Imu | LiDAR 内置 IMU |
| `/cloud_registered` | PointCloud2 | FAST-LIO / Point-LIO |
| `/registered_scan` | PointCloud2 | sensor_scan_generation |
| `/odom` | Odometry | sensor_scan_generation |
| `/scan` | LaserScan | pointcloud_to_laserscan |
| `/cmd_vel` | Twist | Nav2 |
| `/initialpose` | PoseWithCovarianceStamped | RViz |
| `/plan` | Path | Nav2 规划器 |

## 7. 常见问题

**Gazebo 无法启动** — 残留进程阻止新实例启动，手动终止：

```bash
killall -9 gzserver gzclient
```

**LIO 里程计发散** — 检查 IMU 和 LiDAR 话题是否有数据（`ros2 topic echo`），确认 `lidar_type` 与传感器匹配，检查 `use_sim_time` 设置。

**TF 断开 / 代价地图空白** — 使用 `./show_tf_tree.sh` 检查 TF 树，确认 `/scan` 正在发布，检查 `pointcloud_to_laserscan` 的目标坐标系是否与 LiDAR 坐标系一致。

**重定位失败** — 确认 PCD 文件存在且非空，在 RViz 中使用 "2D Pose Estimate" 给出大致初始位姿，或尝试全局重定位方案。

**实机 LiDAR 无数据** — 检查网线连接，确认 `MID360_config.json` 中的 IP 地址，确认 Livox-SDK2 已安装。

**构建失败** — 清理后重新构建：

```bash
rm -rf build/ install/ log/
./build.sh
```

## 8. 致谢

本项目基于以下开源项目构建：

- [FAST-LIO2](https://github.com/hku-mars/FAST_LIO) — 紧耦合 LiDAR-IMU 里程计
- [Point-LIO](https://github.com/hku-mars/Point-LIO) — 高带宽 LiDAR-IMU 里程计
- [Nav2](https://github.com/ros-planning/navigation2) — ROS 2 导航框架
- [small_gicp](https://github.com/koide3/small_gicp) — 高效并行化 GICP 配准
- [KISS-Matcher](https://github.com/MIT-SPARK/KISS-Matcher) — 快速全局点云配准 (ICRA 2025)
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox) — 2D SLAM
- [Livox SDK2](https://github.com/Livox-SDK/Livox-SDK2) — Livox LiDAR SDK
- [Sophus](https://github.com/strasdat/Sophus) — 李群 C++ 库

## 9. 许可证

本项目依据 [MIT License](./LICENSE) 开源。

---