#include "lio_interface/lio_interface.hpp"

namespace lio_interface
{

LioInterface::LioInterface(const rclcpp::NodeOptions & options)
: Node("lio_interface", options){

    this->declare_parameter("odometry_sub", "Odometry");
    this->get_parameter("odometry_sub", odometry_sub_);

    base_frame_to_lidar_initialized_ = false;

    data_position_ = std::make_shared<lio_interface::data_>();

    // 初始化 TF 监听器
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    pcd_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/registered_scan", 5);
    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/registered_odometry", 5);

    pcd_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
        "/cloud_registered", rclcpp::SensorDataQoS(), 
        std::bind(&LioInterface::pointCloudCallback, this, std::placeholders::_1));

    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
        odometry_sub_, rclcpp::SensorDataQoS(),
        std::bind(&LioInterface::odometryCallback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), MAG "LioInterface node is START" RST);
}

LioInterface::~LioInterface(){
    RCLCPP_INFO(this->get_logger(), MAG "LioInterface node is OVER" RST);
}

/**
 * @brief 将 lidar_odom 坐标系下的点云转换到 odom 坐标系下
 *
 * @param[in]  msg 输入的在 lidar_odom 坐标系下的点云（sensor_msgs::PointCloud2）
 * @param[in]  tf_odom_to_lidar_odom_  odom 和 lidar_odom 之间的变换关系（tf2::Transform）
 * @param[out] out odom 坐标系下的点云（sensor_msgs::PointCloud2）
 *
 */
void LioInterface::pointCloudCallback(const sensor_msgs::msg::PointCloud2::ConstSharedPtr msg){

    auto out = std::make_shared<sensor_msgs::msg::PointCloud2>();
    pcl_ros::transformPointCloud("odom", tf_odom_to_lidar_odom_, *msg, *out);
    pcd_pub_->publish(*out);

}

/**
 * @brief 获取 fast-lio 中 camera_init 到 body 的TF变换，获取 base_footprint 到 lidar_frame 的TF变换;
 *        计算 odom 到 lidar_frame 的TF变换，然后将 odom 坐标系下的 lidar_frame 位姿发布到 /lidar_odometry 话题.
 */
void LioInterface::odometryCallback(const nav_msgs::msg::Odometry::ConstSharedPtr msg){

    if (!base_frame_to_lidar_initialized_) {
    try {
        // 从TF树中获取 livox_frame 在 base_footprint 下的位姿 (T_base_footprint_livox)
        auto tf_stamped_tf_base_frame_to_lidar_frame = tf_buffer_->lookupTransform(
            "base_footprint", 
            "livox_frame", 
            tf2::TimePointZero,      
            std::chrono::seconds(1)   
        ); 

        tf2::Transform tf_base_frame_to_lidar_frame;        // base_frame 到 lidar_frame 的TF变换

        // tf2::fromMsg(tf_stamped_lidar_odom_to_lidar_frame.transform, tf_lidar_odom_to_lidar_frame);
        tf2::fromMsg(tf_stamped_tf_base_frame_to_lidar_frame.transform, tf_base_frame_to_lidar_frame);

        // 在初始位置，lidar_frame 到 base_footprint 的静态变换 = odom 到 lidar_odom 的关系
        tf_odom_to_lidar_odom_ = tf_base_frame_to_lidar_frame;

        base_frame_to_lidar_initialized_ = true;
    }   
    catch (const tf2::TransformException & ex) {
        RCLCPP_WARN(this->get_logger(), "TF lookup failed: %s Retrying...", ex.what());
        return;
    }
    }

    tf2::Transform tf_lidar_odom_to_lidar_frame;        // lidar_odom 到 lidar_frame 的变换
    tf2::Transform tf_odom_to_lidar;                    // odom 到 lidar_frame 的变换

    tf2::fromMsg(msg->pose.pose, tf_lidar_odom_to_lidar_frame);

    // 获取 odom 到 lidar_frame 的变换
    tf_odom_to_lidar = tf_odom_to_lidar_odom_ * tf_lidar_odom_to_lidar_frame;

    nav_msgs::msg::Odometry out;
    out.header.stamp = msg->header.stamp;
    out.header.frame_id = "odom";
    out.child_frame_id = "livox_frame";

    const auto & origin = tf_odom_to_lidar.getOrigin();
    out.pose.pose.position.x = origin.x();
    out.pose.pose.position.y = origin.y();
    out.pose.pose.position.z = origin.z();
    out.pose.pose.orientation = tf2::toMsg(tf_odom_to_lidar.getRotation());

    odom_pub_->publish(out);

}

}   // namespace lio_interface

#include "rclcpp_components/register_node_macro.hpp"

RCLCPP_COMPONENTS_REGISTER_NODE(lio_interface::LioInterface)