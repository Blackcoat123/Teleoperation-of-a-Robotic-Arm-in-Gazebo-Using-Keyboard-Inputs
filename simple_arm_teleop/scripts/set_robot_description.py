#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import os

def main():
    rclpy.init()
    node = Node('robot_description_setter')
    
    # Read URDF file
    package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(package_path, 'urdf', 'simple_arm.urdf')
    
    with open(urdf_path, 'r') as f:
        urdf_content = f.read()
    
    # Declare parameter
    node.declare_parameter('robot_description', urdf_content)
    
    print("Robot description parameter set successfully!")
    print("You can now launch robot_state_publisher in another terminal.")
    
    # Keep node alive
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
