#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import xacro
import os
from ament_index_python.packages import get_package_share_directory

class RobotDescriptionPublisher(Node):
    def __init__(self):
        super().__init__('robot_description_publisher')
        
        # Publisher for robot description
        self.description_pub = self.create_publisher(String, '/robot_description', 10)
        
        # Load and process URDF
        self.load_and_publish_urdf()
        
        # Timer to republish periodically (in case someone needs it)
        self.timer = self.create_timer(5.0, self.publish_description)
        
        self.get_logger().info("Robot Description Publisher started!")

    def load_and_publish_urdf(self):
        try:
            # Get package path
            package_path = get_package_share_directory('simple_arm_teleop')
            urdf_path = os.path.join(package_path, 'urdf', 'simple_arm.urdf.xacro')
            
            # If package path doesn't work, try direct path
            if not os.path.exists(urdf_path):
                # Try current working directory structure
                urdf_path = 'src/simple_arm_teleop/urdf/simple_arm.urdf.xacro'
                if not os.path.exists(urdf_path):
                    urdf_path = 'urdf/simple_arm.urdf.xacro'
            
            # Process xacro file
            robot_description = xacro.process_file(urdf_path)
            robot_description_xml = robot_description.toxml()
            
            # Publish the description
            msg = String()
            msg.data = robot_description_xml
            self.description_pub.publish(msg)
            
            self.get_logger().info(f"Published robot description from: {urdf_path}")
            
        except Exception as e:
            self.get_logger().error(f"Failed to load URDF: {e}")
            
            # Fallback - publish a minimal URDF for testing
            minimal_urdf = """<?xml version="1.0"?>
<robot name="simple_arm">
  <link name="base_link"/>
</robot>"""
            msg = String()
            msg.data = minimal_urdf
            self.description_pub.publish(msg)
            self.get_logger().warn("Published minimal fallback URDF")

    def publish_description(self):
        # Republish description periodically
        self.load_and_publish_urdf()

def main(args=None):
    rclpy.init(args=args)
    
    node = RobotDescriptionPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down robot description publisher...")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
