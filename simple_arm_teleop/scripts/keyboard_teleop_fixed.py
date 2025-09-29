#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import threading
import time
import sys

class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop_node')
        
        # Publisher for joint states - USE DIFFERENT TOPIC
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Subscriber to get current joint states from GUI
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10)
        
        # Joint configuration
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.step_size = 0.1
        self.control_active = False
        
        # Joint limits
        self.joint_limits = {
            'joint_1': (-3.14159, 3.14159),
            'joint_2': (-1.57079, 1.57079),
            'joint_3': (-1.57079, 1.57079),
            'joint_4': (-3.14159, 3.14159),
            'joint_5': (-1.57079, 1.57079),
            'joint_6': (-3.14159, 3.14159),
        }
        
        # Only publish when we're actively controlling
        self.timer = self.create_timer(0.05, self.publish_if_active)
        
        self.get_logger().info("🎮 Keyboard Teleop Started!")
        self.print_instructions()
        
        # Start input thread
        self.running = True
        self.input_thread = threading.Thread(target=self.input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def joint_state_callback(self, msg):
        # Update our positions with current state (if not actively controlling)
        if not self.control_active and len(msg.position) >= 6:
            self.joint_positions = list(msg.position[:6])

    def print_instructions(self):
        print("\n" + "="*70)
        print("🦾 KEYBOARD TELEOPERATION - FIXED VERSION")
        print("="*70)
        print("CONTROLS (type letter + ENTER):")
        print("  q/a - Joint 1 (Base)      w/s - Joint 2 (Shoulder)")
        print("  e/d - Joint 3 (Elbow)     r/f - Joint 4 (Wrist roll)")  
        print("  t/g - Joint 5 (Wrist pitch) y/h - Joint 6 (Wrist yaw)")
        print()
        print("  0 - Reset   + - Faster   - - Slower   x - Exit")
        print("="*70)
        print("🎮 Type command + ENTER:")

    def input_loop(self):
        while self.running and rclpy.ok():
            try:
                command = input().strip().lower()
                if command:
                    self.control_active = True  # Take control
                    self.process_command(command)
                    # Stay active for a bit, then release control
                    self.create_timer(2.0, self.release_control)
            except (EOFError, KeyboardInterrupt):
                break

    def release_control(self):
        self.control_active = False

    def process_command(self, command):
        controls = {
            'q': (0, +self.step_size), 'a': (0, -self.step_size),
            'w': (1, +self.step_size), 's': (1, -self.step_size),
            'e': (2, +self.step_size), 'd': (2, -self.step_size),
            'r': (3, +self.step_size), 'f': (3, -self.step_size),
            't': (4, +self.step_size), 'g': (4, -self.step_size),
            'y': (5, +self.step_size), 'h': (5, -self.step_size),
        }
        
        if command in controls:
            joint_idx, delta = controls[command]
            self.move_joint(joint_idx, delta)
        elif command == '0':
            self.joint_positions = [0.0] * 6
            print("🔄 Reset to zero")
        elif command == '+':
            self.step_size = min(0.5, self.step_size + 0.05)
            print(f"📈 Step: {self.step_size:.3f} rad")
        elif command == '-':
            self.step_size = max(0.01, self.step_size - 0.05)
            print(f"📉 Step: {self.step_size:.3f} rad")
        elif command == 'x':
            self.running = False
            rclpy.shutdown()

    def move_joint(self, joint_idx, delta):
        old_pos = self.joint_positions[joint_idx]
        new_pos = old_pos + delta
        
        # Apply limits
        joint_name = self.joint_names[joint_idx]
        min_limit, max_limit = self.joint_limits[joint_name]
        new_pos = max(min_limit, min(max_limit, new_pos))
        
        self.joint_positions[joint_idx] = new_pos
        print(f"🔧 {joint_name}: {new_pos:.3f} rad ({new_pos*57.3:.1f}°)")

    def publish_if_active(self):
        # Only publish when we're actively controlling
        if self.control_active:
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = self.joint_names
            msg.position = self.joint_positions
            msg.velocity = [0.0] * 6
            msg.effort = [0.0] * 6
            self.joint_pub.publish(msg)

def main():
    rclpy.init()
    try:
        node = KeyboardTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except:
            pass
        rclpy.shutdown()

if __name__ == '__main__':
    main()
