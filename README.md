# Smartwarehouse
Smart warehouse with Isaac sim, docker, doosan M0609

Isaac Sim workspace in version 5.0.0 python 3.11

Use build_ros.sh

# 환경 
Docker : Dokerfile 포함
doosan robot2 (예외 : dsr_controller2, dsr_gazebo2, dsr_mujoco, dsr_description2, dsr_hardware2_backup, dsr_example2_backup, dsr_moveit2)

# 빌드 명령어
cd ~/IsaacSim-ros_workspace
chmod +x ./build_ros.sh
git init
sudo ./build_ros.sh

# Change log
0.0.1 : read me edit

# ros 활용
cd ~/IsaacSim-ros_workspaces/humble_ws

# 빌드
colcon build

rosdep install -i --from-path src --rosdistro $ROS_DISTRO -y

# 실행 명령어
build_ws에서 사용
source ~/IsaacSim-ros_workspaces/build_ws/humble/humble_ws/install/local_setup.bash
source ~/IsaacSim-ros_workspaces/build_ws/humble/isaac_sim_ros_ws/install/local_setup.bash \
~/isaacsim/isaac-sim.sh

dsr_controller2_backup   dsr_gazebo2_backup    dsr_mujoco_backup
dsr_description2_backup  dsr_hardware2_backup  fastdds.xml
dsr_example2_backup      dsr_moveit2_backup    src


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

