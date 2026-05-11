# small_gicp_relocalization

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build](https://github.com/SMBU-PolarBear-Robotics-Team/small_gicp_relocalization/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/SMBU-PolarBear-Robotics-Team/small_gicp_relocalization/actions/workflows/build_and_test.yml)

A simple example: Implementing point cloud alignment and localization using [small_gicp](https://github.com/koide3/small_gicp.git)

Given a registered pointcloud (based on the odom frame) and prior pointcloud (mapped using [pointlio](https://github.com/SMBU-PolarBear-Robotics-Team/Point-LIO) or similar tools), the node will calculate the transformation between the two point clouds and publish the correction from the `map` frame to the `odom` frame.

## Dependencies

- ROS2 Humble
- small_gicp
- pcl
- OpenMP

## Build

```zsh
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

git clone https://github.com/SMBU-PolarBear-Robotics-Team/small_gicp_relocalization.git

cd ..
```

1. Install dependencies

    ```zsh
    rosdepc install -r --from-paths src --ignore-src --rosdistro $ROS_DISTRO -y
    ```

2. Build

    ```zsh
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=release
    ```

## Usage

1. Set prior pointcloud file in [launch file](launch/small_gicp_relocalization_launch.py)

2. Adjust the transformation between `base_frame` and `lidar_frame`

    The `global_pcd_map` output by algorithms such as `pointlio` and `fastlio` is strictly based on the `lidar_odom` frame. However, the initial position of the robot is typically defined by the `base_link` frame within the `odom` coordinate system. To address this discrepancy, the code listens for the coordinate transformation from `base_frame`(velocity_reference_frame) to `lidar_frame`, allowing the `global_pcd_map` to be converted into the `odom` coordinate system.

    If not set, empty transformation will be used.

3. Run

    ```zsh
    ros2 launch small_gicp_relocalization small_gicp_relocalization_launch.py
    ```
