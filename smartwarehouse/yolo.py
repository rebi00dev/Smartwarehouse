import rclpy
import numpy as np
import time
from .base_action import BaseAction
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from ultralytics import YOLO
from scipy.spatial.transform import Rotation as R


class YoloDetectAction(BaseAction):
    def __init__(self, node, DR):
        super().__init__(node)
        self.node = node
        self.dr = DR
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')  # YOLO 모델 로드

        self.rgb = None
        self.info = None
        self.depth = None

        self.calib_path = "T_gripper2camera.npy"

        self.rgb_image = self.node.create_subscription(Image,"/rgb",self.rgb_callback,10)
        self.camera_info = self.node.create_subscription(CameraInfo,"/camera_info",self.camera_info_callback,10)
        self.depth_image = self.node.create_subscription(Image,"/depth",self.depth_callback,10)

    def rgb_callback(self,msg):
        self.rgb = msg

    
    def camera_info_callback(self,msg):
        self.info = msg


    def depth_callback(self,msg):
        self.depth = msg

    def execute(self, target_name):
        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.rgb and self.depth and self.info:
                break

        
        
        cv_img = self.bridge.imgmsg_to_cv2(self.rgb, "bgr8")
        depth_img = self.bridge.imgmsg_to_cv2(self.depth, "passthrough")

        results = self.model(cv_img, verbose=False)

        cam_coords = None

        for r in results:
            for box in r.boxes:
                label = self.model.names[int(box.cls[0])]
                if label == target_name:
                    b = box.xyxy[0].to('cpu').numpy()
                    u, v = int((b[0] + b[2]) / 2), int((b[1] + b[3]) / 2)
                    
                    z = self._get_safe_depth(depth_img, u, v)
                    if z > 0:
                        cam_coords = self._project_to_3d(u, v, z, self.info.k)
                        break
            if cam_coords: 
                break
        if cam_coords is None:
            return None

        self.rgb = self.depth = None 
        current_posx, _ = self.dr.get_current_posx()
        base_coords = self.transform_to_base(cam_coords, current_posx)
        
        return target_name, base_coords
            
    
    def transform_to_base(self, camera_coords, robot_posx):
        """카메라 좌표를 로봇 베이스 좌표계로 변환"""
        # 1. 그리퍼로부터 카메라까지의 변환 행렬 (Hand-Eye Calibration)
        T_g2c = np.load(self.calib_path)
        
        # 2. 로봇 베이스로부터 그리퍼까지의 변환 행렬 계산
        x, y, z, rx, ry, rz = robot_posx
        T_b2g = np.eye(4)
        # 두산 로봇은 보통 ZYZ 혹은 XYZ 오일러 각을 사용 (설정에 맞춰 'zyz' 등 수정 필요)
        rot = R.from_euler('zyz', [rx, ry, rz], degrees=True).as_matrix()
        T_b2g[:3, :3] = rot
        T_b2g[:3, 3] = [x, y, z]

        # 3. 최종 변환 행렬: Base -> Camera
        T_b2c = T_b2g @ T_g2c
        
        # 4. 좌표 계산 (Homogeneous Coordinates)
        p_camera = np.array([camera_coords[0], camera_coords[1], camera_coords[2], 1.0])
        p_base = T_b2c @ p_camera
        
        return p_base[:3].tolist()
  
    def _get_safe_depth(self, depth_img, u, v):
        """주변 픽셀 중간값으로 안정적인 깊이 획득"""
        roi = depth_img[max(0, v-2):v+3, max(0, u-2):u+3]
        valid = roi[roi > 0]
        return np.median(valid) if len(valid) > 0 else 0

    def _project_to_3d(self, u, v, z, k):
        """2D -> 3D 투영 수식"""
        fx, cx, fy, cy = k[0], k[2], k[4], k[5]
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        return [float(x), float(y), float(z)]