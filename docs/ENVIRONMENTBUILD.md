# Environment Build Process

**Isaac Sim + ROS2 Humble + Doosan Robot + Vision + Docker**

This project was not only about implementing algorithms, but about **building a complete digital twin warehouse environment from scratch** inside Isaac Sim and integrating it with ROS2 and the Doosan robot API.

The entire system required constructing the simulation scene, configuring robot and gripper models, enabling ROS2 communication, setting up TCP for accurate manipulation, and preparing a vision dataset pipeline for YOLO training.



## 1. USD Warehouse Scene Construction in Isaac Sim

A warehouse environment was manually created using USD assets.

* Warehouse map with shelves and robot base
* Initial attempt included conveyor belts
  * Removed due to frame dorp issue
* Final layout optimized for Pick & Place tasks
* Sensor placement:
  * OAK-D camera mounted on robot arm
  * Additional camera for conveyor/object recognition
  * Removed due to frame dorp issue

This process required understanding Isaac Sim’s USD structure rather than using prebuilt examples.



## 2. Gripper Modeling and URDF → USD Conversion

The project used an OnRobot gripper model provided in ROS2 description format.

Steps performed:

* Parsing XML / URDF / Xacro assets
* Adjusting:

  * joint stiffness
  * damping
  * mimic joints
  * gear ratio
  * joint limits
* Importing into Isaac Sim using URDF Importer
* Combining robot arm and gripper using Robot Assembler
* Final decision: operate entirely in **USD-based structure** instead of URDF

This allowed stable physics simulation and better integration with Isaac Sim.



## 3. ROS2 Communication Architecture Design

ROS2 topics were designed to bridge Isaac Sim, Vision nodes, and the Doosan robot API.

| Component            | ROS2 Topic                           |
| -------------------- | ------------------------------------ |
| Robot Arm Control    | `/dsr01/joint_states`                |
| RGB / Depth Camera   | `/rgb`, `/depth`, `/camera_info`     |
| Gripper              | `/gripper_command`, `/gripper_state` |
| TF                   | `/tf`                                |
| Simulation Time      | `/clock`                             |

The system relied on `use_sim_time` to synchronize Isaac Sim and ROS2 nodes.



## 4. Doosan Robot Bringup & Emulator Integration

To control the robot from ROS2:

* Installed: `ros-humble-topic-based-ros2-control`
* Integrated `doosanrobot2` packages
* Used Doosan Emulator for testing without real hardware
* Solved joint command transmission issue using:

This allowed proper state feedback into the control pipeline.



## 5. TCP (Tool Center Point) Configuration for Accurate Manipulation

Default TCP caused inaccurate Pick positions.

Actions taken:

* Modified `ConfigCreateTcp.srv`
* Created custom TCP for the gripper
* Applied TCP using DSR_ROBOT2 Python API
* Verified pose accuracy between Isaac Sim and robot API

This was critical for precise object manipulation.



## 6. Vision Dataset Generation using Isaac Sim Replicator

A synthetic dataset was generated for YOLO training.

Strategy:

* Fixed object position
* Rotated camera and lighting conditions
* Generated ~1000 images automatically
* Converted dataset using `rep2yolo`
* Trained YOLO inside Docker with GPU access

This created a closed-loop pipeline:
**Isaac Sim → Dataset → YOLO → Robot Action**



## 7. Docker Environment for Training and ROS2 Integration

Docker was configured to enable:

* NVIDIA GPU access
* ROS2 networking using `--net=host`
* YOLO training environment isolation

Without this setup, real-time inference and topic sharing were not possible.



## Outcome

Through this process, a complete integrated environment was achieved where:

* Isaac Sim acts as a digital twin warehouse
* ROS2 manages perception and control
* Doosan API executes robot motion
* Vision model trained from synthetic data drives manipulation

This environment was **entirely constructed from the ground up**, requiring system-level understanding of simulation, robotics middleware, and robot control APIs.
