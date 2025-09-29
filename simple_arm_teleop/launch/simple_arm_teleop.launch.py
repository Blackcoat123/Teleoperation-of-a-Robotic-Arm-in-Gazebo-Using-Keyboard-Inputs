#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    # Get URDF via xacro
    robot_description_content = ParameterValue(
        Command([
            'xacro ', 
            PathJoinSubstitution([
                FindPackageShare('simple_arm_teleop'), 'urdf', 'simple_arm.urdf.xacro'
            ])
        ]),
        value_type=str
    )
    
    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': use_sim_time}
        ],
    )
    
    # Joint Teleoperation Node
    joint_teleop_node = Node(
        package='simple_arm_teleop',
        executable='joint_teleop_node.py',
        name='joint_teleop_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    # RViz (with fallback if config doesn't exist)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    return LaunchDescription([
        # Launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'
        ),
        
        # Nodes
        robot_state_publisher_node,
        joint_teleop_node,
        rviz_node,
    ])
