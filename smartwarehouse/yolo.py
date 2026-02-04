import rclpy
import numpy as np
from .base_action import BaseAction
from sensor_msgs.msg import Image
from ultralytics import YOLO

class YoloDetectAction(BaseAction):
    def __init__(self, node, dr):
        super().__init__()
        self.node = node
        self.dr = dr
        self.model = YOLO('/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/best.pt')

        self.rgb_msg = None
        self.rgb_sub = self.node.create_subscription(Image, "/rgb", self.rgb_callback, 10)
        self.result_pub = self.node.create_publisher(Image, "/yolo_labeled", 10)

    # -------------------- 콜백 --------------------
    def rgb_callback(self, msg):
        self.rgb_msg = msg

    # -------------------- 실행 --------------------
    def execute(self):
        self.node.get_logger().info("YoloAction init")

        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.rgb_msg:
                break

        rgb_img = self.ros_image_to_numpy(self.rgb_msg)

        # YOLO 추론
        results = self.model(rgb_img, verbose=False)

        # 이미지 복사
        annotated_img = rgb_img.copy()

        # 바운딩 박스 + 라벨 그리기
        for r in results:
            for box, conf, cls in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist(), r.boxes.cls.tolist()):
                label = self.model.names[int(cls)]
                x1, y1, x2, y2 = map(int, box)
                self.draw_rectangle(annotated_img, x1, y1, x2, y2,color=(255,0,0))
                self.draw_label(annotated_img, x1, y1, f"{label}:{conf:.2f}")

        # 퍼블리시
        self.publish_result(annotated_img)

    # -------------------- 유틸 --------------------
    def ros_image_to_numpy(self, msg):
        dtype = np.uint8
        channels = 3
        np_arr = np.frombuffer(msg.data, dtype=dtype).reshape((msg.height, msg.width, channels))
        return np_arr

    def draw_rectangle(self, img, x1, y1, x2, y2, color=(255, 255, 255), thickness=1):
        img[y1:y1+thickness, x1:x2] = color  # top
        img[y2-thickness:y2, x1:x2] = color  # bottom
        img[y1:y2, x1:x1+thickness] = color  # left
        img[y1:y2, x2-thickness:x2] = color  # right

    def draw_label(self, img, x, y, text, color=(255, 255, 255)):
        # 글자는 numpy만으로 표현 어렵기 때문에, 텍스트 영역을 색 블록으로 표시
        h, w = img.shape[:2]
        box_w, box_h = min(len(text)*6, w-x), 10
        x2, y2 = x+box_w, y+box_h
        img[y:y2, x:x2] = color  # 배경 색 블록
        # 글자 생략 (numpy만 사용 시) 대신 영역 표시

    def publish_result(self, np_img):
        img_msg = Image()
        img_msg.header.stamp = self.node.get_clock().now().to_msg()
        img_msg.header.frame_id = "camera"
        img_msg.height, img_msg.width = np_img.shape[:2]
        img_msg.encoding = "rgb8"
        img_msg.is_bigendian = 0
        img_msg.step = np_img.shape[1] * 3
        img_msg.data = np_img.tobytes()
        self.result_pub.publish(img_msg)
