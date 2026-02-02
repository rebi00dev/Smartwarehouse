# Smartwarehouse

Smart warehouse simulation using **Isaac Sim**, **Docker**, and **Doosan M0609** robot.  
Isaac Sim workspace version: **5.0.0**, Python **3.11**.  

This project simulates a simple smart warehouse environment with robot manipulation, YOLO-based object detection, and pick & place tasks.

---

## 목차 (Table of Contents)
- [환경](#환경)
- [폴더 구조](#폴더-구조)
- [설치 및 빌드](#설치-및-빌드)
- [ROS 활용](#ros-활용)
- [Docker 실행](#docker-실행)
- [Change Log](#change-log)
- [기여](#기여)
- [라이선스](#라이선스)

    프로젝트 프로그램 설치방법
    프로젝트 프로그램 사용법
---

## 환경 (Environment)
- **Docker** (Dockerfile 포함)
- **Doosan Robot M0609**
- **OnRobot RG2 Gripper**
- **YOLO object detection**
- **Isaac Sim 5.0.0**
- **Python 3.11**
- **ROS2 Humble**

---

## 폴더 구조 (Folder Structure)
```bash
IsaacSim-ros_workspace 
├─ build_ros.sh         # ROS workspace 빌드 스크립트 \
├─ Dockerfile           # Docker 이미지 빌드 \
├─ src/                 # ROS2 패키지 \
├─ launch/              # ROS2 launch 파일 \
├─ urdf/                # 로봇 URDF 파일 \
├─ usd_worlds/          # Isaac Sim USD 환경 파일 \
├─ replicator/          # Isaac Sim Replicator 데이터 \
└─ README.md
```
---

## 설치 및 빌드 (Installation & Build)
1. 저장소 클론
```bash
git clone https://github.com/username/Smartwarehouse.git
cd IsaacSim-ros_workspace
```

2. ROS 빌드 스크립트 권한 설정 및 실행
```bash
chmod +x ./build_ros.sh
sudo ./build_ros.sh
```

3. ROS2 빌드 (Workspace)
```bash
cd ~/IsaacSim-ros_workspaces/humble_ws
colcon build
rosdep install -i --from-path src --rosdistro $ROS_DISTRO -y
```

# 사용 방법 (ROS Usage)
1. 실행 환경 설정
```bash
source ~/IsaacSim-ros_workspaces/build_ws/humble/humble_ws/install/local_setup.bash
source ~/IsaacSim-ros_workspaces/build_ws/humble/isaac_sim_ros_ws/install/local_setup.bash
```
2. Isaac Sim 실행
```bash
  ~/isaacsim/isaac-sim.sh
```
3. Docker 실행 (Docker Example)
Isaac Sim Docker 이미지 실행
```bash
sudo docker run --name isaac-sim -it --rm \
  --runtime=nvidia \
  --network=host \
  -e "ROS_DOMAIN_ID=30" \
  -e "ACCEPT_EULA=Y" \
  -e "DISPLAY=$DISPLAY" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/IsaacSim-ros_workspaces:/workspace \
  isaac_sim_ros:ubuntu_22_humble
```

# Change Log
0.1  : README edit \
0.2  : Add gripper (OnRobot RG2) and assemble with robot arm (Doosan M0609) \
0.3  : Make Environment (USD) \
0.4  : ROS Setting \
0.5  : Delete conveyor \
0.6  : DSR Node setting \
0.7  : DSR Node Modify \
0.8  : DSR Test Code add \
1.0  : Sample Code add \
1.1  : Main Controller code add \
1.2  : Move home code add \
1.3  : Waypoint code add \
1.4  : Pick2conveyor add \
1.5  : Place2shelf add \
1.6  : Setting TCP \
1.7  : Find pose for pose.yaml \
1.8  : Model direction change \
1.9  : Robot renew \
1.10 : Movel test clock pick and place \
2.1  : YOLO data make with Isaac Sim Replicator \
2.2  : Transfer replicator file to YOLO file \
2.3  : YOLO training with Docker \
2.4  : Test best.pt with Docker 

# 기여 (Contributing)

1. 저장소를 Fork 합니다.

2. 새로운 브랜치 생성 (git checkout -b feature/xyz)

3. 코드 변경 후 커밋 (git commit -m "Add new feature")

4. Pull Request 생성

# 라이선스 (License)

MIT License © 2026 DoYoung Kim