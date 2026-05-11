cmake_minimum_required(VERSION 3.10)
project(gld_robot_description)

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

ament_auto_find_build_dependencies()

###########
## 编译 ##
###########

# ament_auto_add_library(${PROJECT_NAME} SHARED
#   src/gld_aruco.cpp
# )

# # opencv需要单独link
# target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})


# rclcpp_components_register_node(${PROJECT_NAME}
#   PLUGIN gld_aruco::GLDAruco     # my_first_node是命名空间，MyNode是类名
#   EXECUTABLE ${PROJECT_NAME}_node
# )

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
  model
  rviz
  launch
)
