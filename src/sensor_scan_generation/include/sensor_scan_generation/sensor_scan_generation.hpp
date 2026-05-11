#ifndef SENSOR_SCAN_GENERATION_HPP
#define SENSOR_SCAN_GENERATION_HPP

#include <memory>
#include <string>

#include "message_filters/subscriber.h"
#include "message_filters/sync_policies/approximate_time.h"
#include "message_filters/synchronizer.h"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_ros/transform_listener.h"
#include "tf2_ros/transform_listener.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "pcl_ros/transforms.hpp"

#define RST  "\033[0m"    
#define BLU  "\033[34m"  
#define MAG  "\033[35m"   

namespace sensor_scan_generation
{

class SensorScanGeneration : public rclcpp::Node
{
public:
    explicit SensorScanGeneration(const rclcpp::NodeOptions & options);
    ~SensorScanGeneration();

private:

    std::string lidar_frame_;
    std::string base_footprint_frame_;
    std::string chassis_frame_;
    tf2::Transform tf_lidar_to_base_footprint_;

    std::unique_ptr<tf2_ros::TransformBroadcaster> br_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_laser_cloud_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr pub_base_footprint_odometry_;

    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;

    message_filters::Subscriber<nav_msgs::msg::Odometry> odometry_sub_;
    message_filters::Subscriber<sensor_msgs::msg::PointCloud2> laser_cloud_sub_;

    using SyncPolicy = message_filters::sync_policies::ApproximateTime<
        nav_msgs::msg::Odometry, sensor_msgs::msg::PointCloud2>;
    std::unique_ptr<message_filters::Synchronizer<SyncPolicy>> sync_;


    void laserCloudAndOdometryHandler(
        const nav_msgs::msg::Odometry::ConstSharedPtr & odometry_msg,
        const sensor_msgs::msg::PointCloud2::ConstSharedPtr & pcd_msg);

    tf2::Transform getTransform(
        const std::string & target_frame, const std::string & source_frame, const rclcpp::Time & time);

    void publishTransform(
        const tf2::Transform & transform, const std::string & parent_frame,
        const std::string & child_frame, const rclcpp::Time & stamp);

    void publishOdometry(
        const tf2::Transform & transform, std::string parent_frame, const std::string & child_frame,
        const rclcpp::Time & stamp);
 
};

} // namespace sensor_scan_generation


# endif