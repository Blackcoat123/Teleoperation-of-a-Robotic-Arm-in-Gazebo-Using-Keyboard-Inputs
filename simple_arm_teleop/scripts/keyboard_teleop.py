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

class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop_node')
        
        # Publisher for joint states  
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint names (must match URDF)
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Movement settings
        self.step_size = 0.1  # radians per key press
        
        # Joint limits
        self.joint_limits = {
            'joint_1': (-3.14159, 3.14159),   # ±180°  
            'joint_2': (-1.57079, 1.57079),   # ±90°
            'joint_3': (-1.57079, 1.57079),   # ±90°
            'joint_4': (-3.14159, 3.14159),   # ±180°
            'joint_5': (-1.57079, 1.57079),   # ±90°
            'joint_6': (-3.14159, 3.14159),   # ±180°
        }
        
        # Timer to publish joint states
        self.timer = self.create_timer(0.05, self.publish_joint_states)  # 20 Hz
        
        # Terminal settings for keyboard input
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.get_logger().info("🎮 Keyboard Teleop Node Started!")
        self.print_instructions()
        
        # Start keyboard input thread
        self.running = True
        self.input_thread = threading.Thread(target=self.keyboard_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def print_instructions(self):
        print("\n" + "="*70)
        print("🦾 KEYBOARD TELEOPERATION - 6DOF ROBOTIC ARM")
        print("="*70)
        print("JOINT CONTROLS:")
        print("  Q/A - Joint 1 (Base rotation)     +/- direction")
        print("  W/S - Joint 2 (Shoulder)          +/- direction") 
        print("  E/D - Joint 3 (Elbow)             +/- direction")
        print("  R/F - Joint 4 (Wrist roll)        +/- direction")
        print("  T/G - Joint 5 (Wrist pitch)       +/- direction")
        print("  Y/H - Joint 6 (Wrist yaw)         +/- direction")
        print()
        print("SPECIAL COMMANDS:")
        print("  0     - Reset all joints to zero position")
        print("  +/=   - Increase step size (faster movement)")
        print("  -/_   - Decrease step size (slower movement)")
        print("  SPACE - Emergency stop (pause movement)")
        print("  ESC   - Exit program")
        print("="*70)
        print(f"Current step size: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
        print("🎮 Ready for keyboard input! Press keys to move joints...")
        print()

    def keyboard_loop(self):
        try:
            tty.setcraw(sys.stdin.fileno())
            
            while self.running and rclpy.ok():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    self.process_key(key)
                time.sleep(0.01)
                    
        except Exception as e:
            self.get_logger().error(f"Keyboard error: {e}")
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

    def process_key(self, key):
        key = key.lower()
        
        # Define joint controls
        controls = {
            'q': (0, +self.step_size),  'a': (0, -self.step_size),  # Joint 1
            'w': (1, +self.step_size),  's': (1, -self.step_size),  # Joint 2
            'e': (2, +self.step_size),  'd': (2, -self.step_size),  # Joint 3
            'r': (3, +self.step_size),  'f': (3, -self.step_size),  # Joint 4
            't': (4, +self.step_size),  'g': (4, -self.step_size),  # Joint 5
            'y': (5, +self.step_size),  'h': (5, -self.step_size),  # Joint 6
        }
        
        if key in controls:
            joint_idx, delta = controls[key]
            self.move_joint(joint_idx, delta)
            
        elif key == '0':
            # Reset all joints to zero
            self.joint_positions = [0.0] * 6
            print("🔄 All joints reset to HOME position (0.0 rad)")
            
        elif key in ['+', '=']:
            # Increase step size
            self.step_size = min(0.5, self.step_size + 0.05)
            print(f"📈 Step size increased: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif key in ['-', '_']:
            # Decrease step size
            self.step_size = max(0.01, self.step_size - 0.05) 
            print(f"📉 Step size decreased: {self.step_size:.3f} rad ({self.step_size*57.3:.1f}°)")
            
        elif key == ' ':
            # Emergency stop
            print("⏸️  EMERGENCY STOP - Movement paused")
            
        elif key == '\x1b':  # ESC key
            print("\n👋 Exiting keyboard teleop...")
            self.running = False
            rclpy.shutdown()

    def move_joint(self, joint_idx, delta):
        joint_name = self.joint_names[joint_idx]
        old_pos = self.joint_positions[joint_idx]
        new_pos = old_pos + delta
        
        # Apply joint limits
        min_limit, max_limit = self.joint_limits[joint_name]
        new_pos = max(min_limit, min(max_limit, new_pos))
        
        # Update position
        self.joint_positions[joint_idx] = new_pos
        
        # Print movement feedback
        direction = "+" if delta > 0 else "-"
        degrees = new_pos * 57.3  # Convert to degrees
        print(f"🔧 {joint_name}: {old_pos:.3f} → {new_pos:.3f} rad ({degrees:.1f}°) [{direction}]")

    def publish_joint_states(self):
        """Continuously publish joint states"""
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
        node = KeyboardTeleopNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutting down keyboard teleop...")
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
