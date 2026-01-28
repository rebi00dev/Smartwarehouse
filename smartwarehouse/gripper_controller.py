import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

class GripperController(Node):
    def __init__(self, open_target=100.0,close_target=0.0):
        super().__init__('gripper_controller')
        # Gripper limit setting ====================================================
        self.open_target = open_target
        self.close_target = close_target
        if not 100 >= open_target >= 0.0:
            self.get_logger().info("gripper open limit over, setting 100.0")
            self.open_target = 100.0
        if not 100 >= close_target >= 0.0:
            self.get_logger().info("gripper close limit over, setting 0.0")
            self.close_target = 0.0
        # parameter setting ========================================================
        self.state = 0.0
        self.reached = False
        self.grasp = False
        self.tolerance = 0.5
        # ROS setting ==============================================================
        self.gripper_command_publisher = self.create_publisher(Float64,"/gripper_command",10)
        self.gripper_state_subscriber = self.create_subscription(Float64,"/gripper_state",self.gripper_state_callback,10)

    
    def gripper_state_callback(self,msg):
        self.state = msg.data

    def open(self):
        self.reached = False
        self.move_gripper(self.open_target)
    
    def close(self):
        self.reached = False
        self.move_gripper(self.close_target)

    def move_gripper(self,target_pose,step=1.0):
        self.grasp = False
        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.05)

            prev_pos = self.state
            diff = target_pose - self.state

            if abs(diff) < self.tolerance:
                self.reached = True
                return True
            
            next_cmd = self.state + (step if diff > 0 else -step)
            next_cmd = max(0.0, min(100.0, next_cmd))
            self.gripper_command_publisher.publish(Float64(data=next_cmd))
            
            time.sleep(0.1)
            rclpy.spin_once(self, timeout_sec=0.05)
            
            # grasp 닫는 중에만 감지 ===================================================================
            if target_pose == self.close_target and abs(prev_pos - self.state) < 0.1:
                if abs(self.state - target_pose) > self.tolerance:
                    self.grasp = True
                    return True 