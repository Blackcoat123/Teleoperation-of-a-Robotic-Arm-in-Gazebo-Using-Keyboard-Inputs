# 🦾 6DOF Robotic Arm Keyboard Teleoperation System

A complete ROS2-based teleoperation system for controlling a 6 degree-of-freedom robotic arm using keyboard inputs, designed for WSL/Linux environments.

## 🎯 Overview

This system provides **direct keyboard control** of individual joints on a 6DOF robotic arm with real-time 3D visualization in RViz. Built from scratch without MoveIt dependencies for maximum simplicity and reliability.

### ✨ Key Features

- ✅ **6 Degrees of Freedom** - Full robotic arm control
- ✅ **Real-time Keyboard Control** - Direct joint-by-joint teleoperation
- ✅ **3D Visualization** - Live robot visualization in RViz
- ✅ **WSL Compatible** - Works perfectly in Windows Subsystem for Linux
- ✅ **Safety Features** - Built-in joint limits and collision geometry
- ✅ **No Complex Dependencies** - No MoveIt, no crashes, pure ROS2
- ✅ **Dual Control Modes** - GUI sliders AND keyboard teleoperation
- ✅ **Smart Conflict Resolution** - Prevents control interference

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Keyboard      │───▶│  Joint Teleop    │───▶│  /joint_states  │
│   Input         │    │  Node            │    │  Topic          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              ▼
│   GUI Sliders   │───▶│ Joint State Pub  │    ┌─────────────────┐
│   (Optional)    │    │ GUI (Optional)   │───▶│ Robot State     │
└─────────────────┘    └──────────────────┘    │ Publisher       │
                                                └─────────────────┘
┌─────────────────┐                                       │
│ URDF Robot      │                                       ▼
│ Description     │────────────────────────────▶┌─────────────────┐
└─────────────────┘                             │   TF Tree       │
                                                │ (Transforms)    │
                                                └─────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────┐
                                                │     RViz2       │
                                                │ 3D Visualization│
                                                └─────────────────┘
```

## 📦 Package Structure

```
simple_arm_teleop/
├── urdf/
│   ├── simple_arm.urdf.xacro      # Original xacro robot description
│   └── simple_arm.urdf            # Plain URDF robot description
├── scripts/
│   ├── simple_keyboard_teleop.py  # Basic keyboard teleop (WSL compatible)
│   ├── keyboard_teleop_fixed.py   # Advanced teleop with conflict resolution
│   └── menu_teleop.py             # Menu-driven control interface
├── launch/
│   ├── test_robot.launch.py       # Main system launcher
│   └── simple_launch.launch.py    # Alternative launcher
├── rviz/
│   └── simple_arm.rviz            # RViz visualization configuration
├── package.xml                     # ROS2 package dependencies
├── CMakeLists.txt                 # Build configuration
└── README.md                      # This documentation
```

## 🚀 Quick Start Guide

### Prerequisites

- **Ubuntu 20.04/22.04** or **WSL2 with Ubuntu**
- **ROS2 Humble** (or compatible)
- **Python 3.8+**

### Installation

1. **Install ROS2 Dependencies**
```bash
sudo apt update
sudo apt install -y \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-tf2-tools
```

2. **Create Workspace and Package**
```bash
# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone or create the simple_arm_teleop package
# (Copy all package files to this directory)
```

3. **Build Package**
```bash
cd ~/ros2_ws
colcon build --packages-select simple_arm_teleop --symlink-install
source install/setup.bash
```

## 🎮 Usage Instructions

### Method 1: Complete System Launch (Recommended)

**Terminal 1: Launch Robot System**
```bash
cd ~/ros2_ws
source install/setup.bash

# Launch robot state publisher and RViz
cp src/simple_arm_teleop/urdf/simple_arm.urdf /tmp/robot.urdf
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat /tmp/robot.urdf)" &
rviz2 &
```

**Terminal 2: Launch Keyboard Control**
```bash
cd ~/ros2_ws
source install/setup.bash

# Use the conflict-resolution version
python3 src/simple_arm_teleop/scripts/keyboard_teleop_fixed.py
```

### Method 2: GUI + Keyboard Control

**Terminal 1: Full System with GUI**
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch simple_arm_teleop test_robot.launch.py
```

**Terminal 2: Keyboard Override**
```bash
cd ~/ros2_ws
source install/setup.bash
python3 src/simple_arm_teleop/scripts/keyboard_teleop_fixed.py
```

## 🎯 Control Interface

### Keyboard Controls

```
🎮 KEYBOARD TELEOPERATION CONTROLS
═══════════════════════════════════════════════════════════════════

JOINT CONTROLS (type letter + ENTER):
  q + [ENTER] - Joint 1 (Base) rotate left     a + [ENTER] - rotate right
  w + [ENTER] - Joint 2 (Shoulder) up          s + [ENTER] - down  
  e + [ENTER] - Joint 3 (Elbow) extend         d + [ENTER] - retract
  r + [ENTER] - Joint 4 (Wrist roll) +         f + [ENTER] - -
  t + [ENTER] - Joint 5 (Wrist pitch) up       g + [ENTER] - down
  y + [ENTER] - Joint 6 (Wrist yaw) left       h + [ENTER] - right

SPECIAL COMMANDS:
  0 + [ENTER] - Reset all joints to zero position
  + + [ENTER] - Increase movement step size (faster)
  - + [ENTER] - Decrease movement step size (slower) 
  x + [ENTER] - Exit teleoperation program

═══════════════════════════════════════════════════════════════════
```

### Joint Configuration

| Joint | Name | Type | Range | Function |
|-------|------|------|-------|-----------|
| 1 | Base | Revolute | ±180° | Base rotation |
| 2 | Shoulder | Revolute | ±90° | Arm up/down |
| 3 | Elbow | Revolute | ±90° | Arm bend |
| 4 | Wrist Roll | Revolute | ±180° | Wrist rotation |
| 5 | Wrist Pitch | Revolute | ±90° | Wrist up/down |
| 6 | End Effector | Revolute | ±180° | Final rotation |

## 🔧 Configuration

### Adjusting Movement Speed
The step size determines how much each joint moves per command:
- **Default**: 0.1 radians (~5.7°)
- **Range**: 0.01 to 0.5 radians
- **Control**: Use `+` and `-` commands during operation

### RViz Setup
1. **Add RobotModel Display**:
   - Click "Add" → "RobotModel"
   - Set "Description Topic" to `/robot_description`
   
2. **Add TF Display**:
   - Click "Add" → "TF"
   - Enable "Show Names" and "Show Axes"
   
3. **Set Fixed Frame**:
   - In Global Options, set "Fixed Frame" to `base_link`

## 🐛 Troubleshooting

### Common Issues and Solutions

**Problem: Robot flipping/oscillating between positions**
```bash
# Solution: Kill conflicting joint state publishers
pkill -f joint_state_publisher_gui
# Then restart with only one control method
```

**Problem: "No transform" errors in RViz**
```bash
# Check if joint states are publishing
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states

# Verify robot state publisher is running
ros2 node list | grep robot_state_publisher
```

**Problem: Keyboard input not working in WSL**
```bash
# Use the WSL-compatible version
python3 src/simple_arm_teleop/scripts/simple_keyboard_teleop.py
# (Requires typing letter + ENTER for each command)
```

**Problem: Robot not visible in RViz**
```bash
# Check robot description topic
ros2 topic echo /robot_description --once

# Verify URDF file exists and is valid
cat src/simple_arm_teleop/urdf/simple_arm.urdf
```

### Diagnostic Commands

```bash
# System health check
ros2 node list                    # Check running nodes
ros2 topic list | grep joint      # Check joint topics
ros2 topic info /joint_states     # Check publishers/subscribers
ros2 run tf2_tools view_frames     # Generate TF tree
```

## 📊 System Specifications

- **Degrees of Freedom**: 6 (6DOF)
- **Control Rate**: 20 Hz joint state publishing
- **Joint Limits**: Realistic ranges per joint type
- **Safety Features**: Software joint limits, collision geometry
- **Visualization**: Real-time 3D rendering at 30 FPS
- **Compatibility**: ROS2 Humble, Ubuntu 20.04+, WSL2

## 🎓 Educational Value

This system demonstrates:
- **ROS2 Package Development** - Complete package structure and build system
- **URDF Robot Modeling** - 3D robot description with collision geometry
- **Node Communication** - Publishers, subscribers, and message passing
- **Transform Systems** - TF2 coordinate frame management
- **Real-time Control** - Joint state publishing and robot control
- **Visualization** - RViz configuration and 3D robot display

## 🚀 Extensions and Future Development

### Potential Enhancements
- **Trajectory Planning** - Smooth path execution between waypoints
- **Inverse Kinematics** - End-effector position control
- **Force Control** - Compliance and interaction control
- **Gazebo Simulation** - Physics-based simulation environment
- **Camera Integration** - Visual servoing and perception
- **Path Recording** - Teach and repeat functionality

### Hardware Integration
- **Real Robot Control** - Adapt for actual robotic hardware
- **Sensor Integration** - Add encoders, force sensors, cameras
- **Safety Systems** - Emergency stops, collision detection
- **Communication Interfaces** - Serial, CAN, Ethernet connectivity

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review ROS2 documentation
- Test with minimal configurations first
- Use diagnostic commands to identify problems

## 🏆 Acknowledgments

- Built with ROS2 framework
- Uses standard robotics conventions
- Designed for educational and research purposes
- Compatible with WSL for Windows developers

---

**🎉 Congratulations on building your own 6DOF robotic arm teleoperation system!** 🦾

*Happy teleoperating!* 🎮