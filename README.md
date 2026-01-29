# Smartwarehouse
Smart warehouse with Isaac sim, docker, doosan M0609 \

Isaac Sim workspace in version 5.0.0 python 3.11 \

Use build_ros.sh \

# 환경 
Docker : Dokerfile 포함 \
doosan robot2 (예외 : dsr_controller2, dsr_gazebo2, dsr_mujoco, dsr_description2, dsr_hardware2_backup, dsr_example2_backup, dsr_moveit2) \

# 빌드 명령어
cd ~/IsaacSim-ros_workspace \
chmod +x ./build_ros.sh \
git init \
sudo ./build_ros.sh \

# Change log
0.1 : read me edit \
0.2 : add gripper (onrobot rg2) and assemble with robot arm (doosan robot M0609) \
0.3 : make Enviornment(USD) \ 
0.4 : ROS_Setting \
0.5 : Delete conveyor \
0.6 : DSR Node setting \
0.7 : DSR Node Modify \
0.8 : DSR Test Code add \
1.0 : Sample Code add \
1.1 : Main Controller code add \
1.2 : Move home code add \
1.3 : Waypoint code add \
1.3 : Pick2conveyor add \
# ros 활용
cd ~/IsaacSim-ros_workspaces/humble_ws \

# 빌드
colcon build

rosdep install -i --from-path src --rosdistro $ROS_DISTRO -y \

# 실행 명령어
build_ws에서 사용 \
source ~/IsaacSim-ros_workspaces/build_ws/humble/humble_ws/install/local_setup.bash \
source ~/IsaacSim-ros_workspaces/build_ws/humble/isaac_sim_ros_ws/install/local_setup.bash \
~/isaacsim/isaac-sim.sh \


# docker 실행 예시, Isaac sim 이미지 실행
sudo docker run --name isaac-sim -it --rm \
  --runtime=nvidia \
  --network=host \
  -e "ROS_DOMAIN_ID=30" \
  -e "ACCEPT_EULA=Y" \
  -e "DISPLAY=$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/IsaacSim-ros_workspaces:/workspace \
  isaac_sim_ros:ubuntu_22_humble

