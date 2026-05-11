#ifndef LIO_INTERFACE_HPP
#define LIO_INTERFACE_HPP

#include <memory>
#include <string>

#include "nav_msgs/msg/odometry.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include "pcl_ros/transforms.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

#include "lio_interface/packet.hpp"

#define RST  "\033[0m"    /* Reset to default color */
#define BLU  "\033[34m"   /* Blue */
#define MAG  "\033[35m"   /* Magenta */

namespace lio_interface
{

class LioInterface : public rclcpp::Node
{
public:
    explicit LioInterface(const rclcpp::NodeOptions & options);
    ~LioInterface() override;

private:

    std::string odometry_sub_;

    bool base_frame_to_lidar_initialized_;
    
    std::shared_ptr<lio_interface::data_> data_position_;
    tf2::Transform tf_odom_to_lidar_odom_;  // odom 到 lidar_odom 的TF变换

    void pointCloudCallback(const sensor_msgs::msg::PointCloud2::ConstSharedPtr msg);
    void odometryCallback(const nav_msgs::msg::Odometry::ConstSharedPtr msg);

    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr pcd_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pcd_pub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;

    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

};

}

#endif  // LIO_INTERFACE_HPP