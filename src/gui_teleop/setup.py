from setuptools import setup

package_name = 'gui_teleop'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dev',
    maintainer_email='dev@todo.todo',
    description='GUI keyboard teleop controller for ROS 2',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gui_teleop_node = gui_teleop.gui_teleop_node:main',
        ],
    },
)
