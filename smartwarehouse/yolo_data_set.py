import os
import glob
import random
import shutil

SRC_DIR = "/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/yolo_data_output"
YOLO_TXT_DIR = os.path.join(SRC_DIR, "yolo_format")

DATASET_DIR = os.path.join(SRC_DIR, "dataset")

train_img = os.path.join(DATASET_DIR, "images/train")
val_img = os.path.join(DATASET_DIR, "images/val")
train_lbl = os.path.join(DATASET_DIR, "labels/train")
val_lbl = os.path.join(DATASET_DIR, "labels/val")

for d in [train_img, val_img, train_lbl, val_lbl]:
    os.makedirs(d, exist_ok=True)

png_files = sorted(glob.glob(os.path.join(SRC_DIR, "rgb_*.png")))
random.shuffle(png_files)

split_idx = int(len(png_files) * 0.8)
train_files = png_files[:split_idx]
val_files = png_files[split_idx:]

def move(files, img_dst, lbl_dst):
    for img_path in files:
        name = os.path.basename(img_path).split("_")[1].split(".")[0]
        txt_path = os.path.join(YOLO_TXT_DIR, f"{name}.txt")

        shutil.copy(img_path, os.path.join(img_dst, f"{name}.png"))
        shutil.copy(txt_path, os.path.join(lbl_dst, f"{name}.txt"))

move(train_files, train_img, train_lbl)
move(val_files, val_img, val_lbl)

print("✅ train/val 분할 완료")
