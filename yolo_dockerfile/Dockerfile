FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install ultralytics

WORKDIR /workspace

RUN apt update && apt install -y libgl1 libglib2.0-0 libsm6 libxrender1 libxext6
