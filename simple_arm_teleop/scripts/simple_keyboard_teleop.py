#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import threading
import time
import sys

class SimpleKeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('simple_keyboard_teleop_node')
        
        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint configuration
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.step_size = 0.1
        
        # Joint limits
        self.joint_limits = {
            'joint_1': (-3.14159, 3.14159),
            'joint_2': (-1.57079, 1.57079),
            'joint_3': (-1.57079, 1.57079),
            'joint_4': (-3.14159, 3.14159),
            'joint_5': (-1.57079, 1.57079),
            'joint_6': (-3.14159, 3.14159),
        }
        
        # Publishing timer
        self.timer = self.create_timer(0.05, self.publish_joint_states)
        
        self.get_logger().info("🎮 Simple Keyboard Teleop Started!")
        self.print_instructions()
        
        # Start input thread
        self.running = True
        self.input_thread = threading.Thread(target=self.input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def print_instructions(self):
        print("\n" + "="*70)
        print("🦾 SIMPLE KEYBOARD TELEOPERATION - 6DOF ROBOTIC ARM")
        print("="*70)
        print("JOINT CONTROLS (press ENTER after each key):")
        print("  q/a - Joint 1 (Base rotation)     +/- direction")
        print("  w/s - Joint 2 (Shoulder)          +/- direction") 
        print("  e/d - Joint 3 (Elbow)             +/- direction")
        print("  r/f - Joint 4 (Wrist roll)        +/- direction")
        print("  t/g - Joint 5 (Wrist pitch)       +/- direction")
        print("  y/h - Joint 6 (Wrist yaw)         +/- direction")
        print()
        print("SPECIAL COMMANDS:")
        print("  0     - Reset all joints to zero")
        print("  +     - Increase step size")
        print("  -     - Decrease step size")
        print("  x     - Exit program")
        print("="*70)
        print(f"Current step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
        print("🎮 Type a command and press ENTER:")

    def input_loop(self):
        while self.running and rclpy.ok():
            try:
                # Simple input - works in WSL
                command = input().strip().lower()
                self.process_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.get_logger().error(f"Input error: {e}")

    def process_command(self, command):
        if not command:
            return
            
        # Joint controls
        controls = {
            'q': (0, +self.step_size),  'a': (0, -self.step_size),  # Joint 1
            'w': (1, +self.step_size),  's': (1, -self.step_size),  # Joint 2
            'e': (2, +self.step_size),  'd': (2, -self.step_size),  # Joint 3
            'r': (3, +self.step_size),  'f': (3, -self.step_size),  # Joint 4
            't': (4, +self.step_size),  'g': (4, -self.step_size),  # Joint 5
            'y': (5, +self.step_size),  'h': (5, -self.step_size),  # Joint 6
        }
        
        if command in controls:
            joint_idx, delta = controls[command]
            self.move_joint(joint_idx, delta)
            
        elif command == '0':
            self.joint_positions = [0.0] * 6
            print("🔄 All joints reset to HOME position")
            
        elif command == '+':
            self.step_size = min(0.5, self.step_size + 0.05)
            print(f"📈 Step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif command == '-':
            self.step_size = max(0.01, self.step_size - 0.05)
            print(f"📉 Step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif command == 'x':
            print("\n👋 Exiting...")
            self.running = False
            rclpy.shutdown()
            
        else:
            print(f"❓ Unknown command: '{command}'. Try q/a, w/s, e/d, r/f, t/g, y/h, 0, +, -, or x")

    def move_joint(self, joint_idx, delta):
        joint_name = self.joint_names[joint_idx]
        old_pos = self.joint_positions[joint_idx]
        new_pos = old_pos + delta
        
        # Apply joint limits
        min_limit, max_limit = self.joint_limits[joint_name]
        new_pos = max(min_limit, min(max_limit, new_pos))
        
        self.joint_positions[joint_idx] = new_pos
        
        # Print feedback
        direction = "+" if delta > 0 else "-"
        degrees = new_pos * 57.3
        print(f"🔧 {joint_name}: {old_pos:.3f} → {new_pos:.3f} rad ({degrees:.1f}°) [{direction}]")

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        msg.name = self.joint_names
        msg.position = self.joint_positions
        msg.velocity = [0.0] * len(self.joint_names)
        msg.effort = [0.0] * len(self.joint_names)
        
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = SimpleKeyboardTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        try:
            node.running = False
            node.destroy_node()
        except:
            pass
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
