import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class VisionManager(Node):
    def __init__(self):
        super().__init__('vision_manager')
        self._target_object = None
        # YOLO 토픽 구독 (타입은 실제 YOLO 출력에 맞춰 String/Int32 등 선택)
        self.create_subscription(String, '/detected_object', self._yolo_callback, 10)
        self.get_logger().info("Vision Manager 준비 완료")

    def _yolo_callback(self, msg):
        # 로봇이 작업 중이 아닐 때(None)만 새로운 물체 정보를 기록
        if self._target_object is None:
            self._target_object = msg.data
            self.get_logger().info(f"새로운 물체 감지: {self._target_object}")

    def get_target(self):
        """현재 감지된 물체 반환"""
        return self._target_object

    def clear_target(self):
        """작업 완료 후 데이터 초기화"""
        self._target_object = None