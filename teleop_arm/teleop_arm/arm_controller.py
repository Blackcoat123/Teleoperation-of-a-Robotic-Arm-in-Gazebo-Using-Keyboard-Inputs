#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')

        # Names of your 6 joints (replace with your robot's joint names)
        self.joint_names = ['j1','j2','j3','j4','j5','j6']
        self.joint_positions = [0.0] * 6  # initial joint positions

        # Publisher for joint states
        self.pub = self.create_publisher(JointState, 'joint_states', 10)

        # Subscriber to teleop velocity commands
        self.sub = self.create_subscription(
            Twist,
            'arm_velocity_command',
            self.cmd_callback,
            10
        )

        # Timer to publish joint states at 50 Hz
        self.timer = self.create_timer(0.02, self.publish_joints)

        self.vel_scale = 0.05  # how fast joints move per keypress

    def cmd_callback(self, msg: Twist):
        # Map Twist linear/ang to joint increments
        self.joint_positions[0] += msg.linear.x * self.vel_scale
        self.joint_positions[1] += msg.linear.y * self.vel_scale
        self.joint_positions[2] += msg.linear.z * self.vel_scale
        self.joint_positions[3] += msg.angular.x * self.vel_scale
        self.joint_positions[4] += msg.angular.y * self.vel_scale
        self.joint_positions[5] += msg.angular.z * self.vel_scale

    def publish_joints(self):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names
        js.position = self.joint_positions
        self.pub.publish(js)

def main(args=None):
    rclpy.init(args=args)
    node = ArmController()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
