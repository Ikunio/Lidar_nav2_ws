#ifndef GLOBAL_RELOCALIZATION_HPP
#define GLOBAL_RELOCALIZATION_HPP

#include <memory>
#include <string>
#include <vector>

#include "pcl/common/transforms.h"
#include "pcl_conversions/pcl_conversions.h"
#include "small_gicp/pcl/pcl_registration.hpp"
#include "small_gicp/util/downsampling_omp.hpp"
#include "tf2_eigen/tf2_eigen.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "pcl/io/pcd_io.h"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "small_gicp/ann/kdtree_omp.hpp"
#include "small_gicp/factors/gicp_factor.hpp"
#include "small_gicp/pcl/pcl_point.hpp"
#include "small_gicp/registration/reduction_omp.hpp"
#include "small_gicp/registration/registration.hpp"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_ros/transform_listener.h"

#define RST  "\033[0m"    /* Reset to default color */
#define BLU  "\033[34m"   /* Blue */
#define MAG  "\033[35m"   /* Magenta */

namespace global_relocalization
{

class GlobalRelocalization : public rclcpp::Node
{
public:
  explicit GlobalRelocalization();
  ~GlobalRelocalization();

private:

  float max_dist_sq_;

  std::string map_frame_;
  std::string odom_frame_;
  std::string robot_base_frame_;

  std::string current_scan_frame_id_;
  rclcpp::Time last_scan_time_;

  std::string base_frame_;
  std::string lidar_frame_;

  std::vector<double> init_pose_;
  std::string prior_pcd_file_;

  float global_leaf_size_;
  float registered_leaf_size_;

  int num_threads_;
  int num_neighbors_;

  pcl::PointCloud<pcl::PointCovariance>::Ptr target_;
  pcl::PointCloud<pcl::PointCovariance>::Ptr source_;

  std::shared_ptr<small_gicp::KdTree<pcl::PointCloud<pcl::PointCovariance>>> target_tree_;
  std::shared_ptr<small_gicp::KdTree<pcl::PointCloud<pcl::PointCovariance>>> source_tree_;

  pcl::PointCloud<pcl::PointXYZ>::Ptr accumulated_cloud_; // 实时累积点云
  pcl::PointCloud<pcl::PointXYZ>::Ptr global_map_;        // pcd点云图
  std::shared_ptr<
    small_gicp::Registration<small_gicp::GICPFactor, small_gicp::ParallelReductionOMP>>
    register_;

  Eigen::Isometry3d result_t_;
  Eigen::Isometry3d previous_result_t_;


  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr pcd_sub_;
  rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr initial_pose_sub_;

  rclcpp::TimerBase::SharedPtr transform_timer_;
  rclcpp::TimerBase::SharedPtr register_timer_;

  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::unique_ptr<tf2_ros::TransformListener> tf_listener_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

  void registeredPcdCallback(const sensor_msgs::msg::PointCloud2::ConstSharedPtr msg);
  void loadGlobalMap(const std::string & file_name);
  void performRegistration();
  void publishTransform();
  void initialPoseCallback(const geometry_msgs::msg::PoseWithCovarianceStamped::ConstSharedPtr msg);

};

}  // namespace global_relocalization

#endif  // GLOBAL_RELOCALIZATION_HPP