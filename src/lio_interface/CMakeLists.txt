cmake_minimum_required(VERSION 3.10)
project(lio_interface)

## Use C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 只要有编译警告就当作错误处理
add_definitions(-Wall -Werror)

# 防止Vscode头文件报红
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

#######################
## 去package.xml查找依赖 ##
#######################

find_package(ament_cmake_auto REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

ament_auto_find_build_dependencies()

###########
## 编译 ##
###########

ament_auto_add_library(${PROJECT_NAME} SHARED
  DIRECTORY src
)

# 显式链接 tf2_geometry_msgs (提供 tf2::fromMsg 等函数)
target_link_libraries(${PROJECT_NAME} tf2_geometry_msgs::tf2_geometry_msgs)

# 为每个组件注册单独的可执行节点
rclcpp_components_register_node(${PROJECT_NAME}
  PLUGIN "lio_interface::LioInterface"
  EXECUTABLE lio_interface_node
)

#############
## 测试 ##
#############

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  list(APPEND AMENT_LINT_AUTO_EXCLUDE
    ament_cmake_copyright
    ament_cmake_uncrustify
  )
  ament_lint_auto_find_test_dependencies()
endif()

#############
## 加载到install中 ##
#############

ament_auto_package(
  INSTALL_TO_SHARE
  config
  launch
)
