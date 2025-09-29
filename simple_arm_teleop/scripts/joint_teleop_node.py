#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import sys
import select
import tty
import termios
import threading
import time

class JointTeleopNode(Node):
    def __init__(self):
        super().__init__('joint_teleop_node')
        
        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint names MUST match URDF exactly
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Movement step size (radians)
        self.step_size = 0.1
        
        # Joint limits (in radians)
        self.joint_limits = {
            'joint_1': (-3.14159, 3.14159),
            'joint_2': (-1.57079, 1.57079),
            'joint_3': (-1.57079, 1.57079),
            'joint_4': (-3.14159, 3.14159),
            'joint_5': (-1.57079, 1.57079),
            'joint_6': (-3.14159, 3.14159),
        }
        
        # Timer to publish joint states at high frequency
        self.timer = self.create_timer(0.02, self.publish_joint_states)  # 50 Hz
        
        # Initialize terminal for keyboard input
        if sys.stdin.isatty():
            self.settings = termios.tcgetattr(sys.stdin)
            self.setup_keyboard_input()
        
        self.get_logger().info("🦾 Joint Teleoperation Node Started!")
        self.print_instructions()

    def setup_keyboard_input(self):
        # Start keyboard input thread
        self.running = True
        self.input_thread = threading.Thread(target=self.keyboard_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def print_instructions(self):
        print("\n" + "="*60)
        print("🦾 JOINT-BY-JOINT KEYBOARD CONTROL")
        print("="*60)
        print("Controls:")
        print("  Q/A - Joint 1 (Base rotation)     +/-")
        print("  W/S - Joint 2 (Shoulder)          +/-") 
        print("  E/D - Joint 3 (Elbow)             +/-")
        print("  R/F - Joint 4 (Wrist roll)        +/-")
        print("  T/G - Joint 5 (Wrist pitch)       +/-")
        print("  Y/H - Joint 6 (Wrist yaw)         +/-")
        print()
        print("  0   - Reset all joints to zero")
        print("  +/- - Increase/decrease step size")
        print("  ESC - Exit")
        print("="*60)
        print(f"Current step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
        print("Ready for input...")
        print("Publishing joint states at 50 Hz...")

    def keyboard_input_loop(self):
        try:
            tty.setcraw(sys.stdin.fileno())
            
            while self.running and rclpy.ok():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    self.process_key(key)
                time.sleep(0.01)
                
        except Exception as e:
            self.get_logger().error(f"Keyboard input error: {e}")
        finally:
            # Restore terminal settings
            if hasattr(self, 'settings'):
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

    def process_key(self, key):
        key = key.lower()
        
        # Joint controls
        joint_controls = {
            'q': (0, self.step_size),   'a': (0, -self.step_size),
            'w': (1, self.step_size),   's': (1, -self.step_size),
            'e': (2, self.step_size),   'd': (2, -self.step_size),
            'r': (3, self.step_size),   'f': (3, -self.step_size),
            't': (4, self.step_size),   'g': (4, -self.step_size),
            'y': (5, self.step_size),   'h': (5, -self.step_size),
        }
        
        if key in joint_controls:
            joint_idx, delta = joint_controls[key]
            self.move_joint(joint_idx, delta)
            
        elif key == '0':
            self.joint_positions = [0.0] * 6
            print("🔄 All joints reset to zero")
            
        elif key == '+' or key == '=':
            self.step_size = min(0.5, self.step_size + 0.05)
            print(f"📈 Step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif key == '-' or key == '_':
            self.step_size = max(0.01, self.step_size - 0.05)
            print(f"📉 Step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif key == '\x1b':  # ESC key
            print("\n👋 Exiting...")
            self.running = False
            rclpy.shutdown()

    def move_joint(self, joint_idx, delta):
        joint_name = self.joint_names[joint_idx]
        old_pos = self.joint_positions[joint_idx]
        new_pos = old_pos + delta
        
        # Apply joint limits
        min_limit, max_limit = self.joint_limits[joint_name]
        new_pos = max(min_limit, min(max_limit, new_pos))
        
        self.joint_positions[joint_idx] = new_pos
        
        # Print status
        direction = "+" if delta > 0 else "-"
        print(f"🔧 {joint_name}: {old_pos:.3f} → {new_pos:.3f} rad ({direction}{abs(delta):.3f})")

    def publish_joint_states(self):
        """Publish joint states continuously"""
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
        node = JointTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean shutdown
        try:
            node.destroy_node()
        except:
            pass
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
