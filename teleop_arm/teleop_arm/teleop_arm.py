#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, termios, tty

# Key bindings: change these to move joints
key_bindings = {
    'q': [1,0,0,0,0,0],
    'a': [-1,0,0,0,0,0],
    'w': [0,1,0,0,0,0],
    's': [0,-1,0,0,0,0],
    'e': [0,0,1,0,0,0],
    'd': [0,0,-1,0,0,0],
    'r': [0,0,0,1,0,0],
    'f': [0,0,0,-1,0,0],
    't': [0,0,0,0,1,0],
    'g': [0,0,0,0,-1,0],
    'y': [0,0,0,0,0,1],
    'h': [0,0,0,0,0,-1]
}

def getKey():
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopArm(Node):
    def __init__(self):
        super().__init__('teleop_arm')
        self.pub = self.create_publisher(Twist, 'arm_velocity_command', 10)

    def run(self):
        print("Use keys to move joints (q/a w/s e/d r/f t/g y/h), CTRL-C to quit")
        while True:
            key = getKey()
            twist = Twist()
            if key in key_bindings:
                vals = key_bindings[key]
                twist.linear.x = vals[0]
                twist.linear.y = vals[1]
                twist.linear.z = vals[2]
                twist.angular.x = vals[3]
                twist.angular.y = vals[4]
                twist.angular.z = vals[5]
                self.pub.publish(twist)
            elif key == '\x03':
                break

def main(args=None):
    global settings
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init(args=args)
    node = TeleopArm()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()
