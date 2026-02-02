# 1. NVIDIA CUDA + Ubuntu 22.04 기반 (기존 유지)
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# 2. 필수 시스템 패키지 설치
# libgl1-mesa-glx 및 libqt5gui5 등 GUI 관련 라이브러리 추가
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libqt5gui5 \
    && rm -rf /var/lib/apt/lists/*

# 3. pip 업그레이드 및 의존성 패키지 설치
RUN pip3 install --upgrade pip

# [핵심] 의존성 충돌 해결: numpy 버전을 2.0 미만으로 강제 고정
# ultralytics 설치 시 자동으로 numpy 최신버전이 깔리는 것을 방지하기 위해 먼저 설치하거나 명시합니다.
RUN pip3 install --no-cache-dir "numpy<2"
RUN pip3 install --no-cache-dir ultralytics opencv-python scipy

# 4. ROS2와 연동할 경우 cv_bridge 등 추가 (선택 사항)
# RUN pip3 install cv_bridge 

WORKDIR /workspace

# 5. 환경 변수 설정 (GUI 렌더링 관련)
ENV QT_X11_NO_MITSHM=1
