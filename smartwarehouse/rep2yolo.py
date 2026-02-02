import os
import glob
import numpy as np
import cv2

SRC_DIR = "/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/yolo_data_output"
YOLO_DIR = os.path.join(SRC_DIR, "yolo_format")
os.makedirs(YOLO_DIR, exist_ok=True)

# semanticId 고정 매핑 (도영님 환경)
id_to_class = {
    0: "dice",
    1: "lemon",
    2: "clock"
}
class_to_id = {v: i for i, v in id_to_class.items()}

png_files = sorted(glob.glob(os.path.join(SRC_DIR, "rgb_*.png")))

for png_file in png_files:
    idx = os.path.basename(png_file).split("_")[1].split(".")[0]
    npy_file = os.path.join(SRC_DIR, f"bounding_box_2d_tight_{idx}.npy")

    if not os.path.exists(npy_file):
        continue

    img = cv2.imread(png_file)
    h, w, _ = img.shape

    bbox = np.load(npy_file)

    lines = []

    for b in bbox:
        sid = int(b["semanticId"])
        x1, y1, x2, y2 = b["x_min"], b["y_min"], b["x_max"], b["y_max"]

        cx = ((x1 + x2) / 2) / w
        cy = ((y1 + y2) / 2) / h
        bw = (x2 - x1) / w
        bh = (y2 - y1) / h

        class_id = class_to_id[id_to_class[sid]]
        lines.append(f"{class_id} {cx} {cy} {bw} {bh}")

    with open(os.path.join(YOLO_DIR, f"{idx}.txt"), "w") as f:
        f.write("\n".join(lines))

print("✅ YOLO 변환 완료")
