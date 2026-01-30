import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
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
        # Joint State setting ======================================================
        self.gripper_name = 'finger_width'
        self.open_pos = -1.0
        self.close_pos = -3.0
        self.effort = 0
        # ROS setting ==============================================================
        self.gripper_command_publisher = self.create_publisher(JointState,"/gripper_command",10)
        self.gripper_state_subscriber = self.create_subscription(JointState,"/gripper_state",self.gripper_state_callback,10)

    def state2percent(self,pos):
        return max(
            0.0,
            min(
                100.0,
                100.0 * (pos - self.close_pos)
                / (self.open_pos - self.close_pos)
            )
        )
    def percent2state(self,percent):
        return self.close_pos + \
            (percent / 100.0) * (self.open_pos - self.close_pos)
    

    def gripper_state_callback(self,msg):
        if self.gripper_name not in msg.name:
            return

        idx = msg.name.index(self.gripper_name)
        joint_pos = msg.position[idx]
        self.effort = msg.effort[idx]
        
        self.state = self.state2percent(joint_pos)


    def open(self):
        self.grasp = False
        self.move_gripper(self.open_target)
    
    def close(self):
        self.move_gripper(self.close_target)

    def move_gripper(self,target_pose,step=5.0):
        self.reached = False

        rclpy.spin_once(self, timeout_sec=0.05)

        diff = target_pose - self.state
        # if self.effort > 0.01 and self.state < -2.0:
        #     self.grasp = True
        # else:
            # self.grasp = False
        if abs(diff) < self.tolerance or self.grasp:
            self.reached = True
            return True

        
        next_cmd = self.state + (step if diff > 0 else -step)
        next_cmd = max(0.0, min(100.0, next_cmd))

        joint_cmd = JointState()
        joint_cmd.name = [self.gripper_name]
        joint_cmd.position = [self.percent2state(next_cmd)]
        self.gripper_command_publisher.publish(joint_cmd)
        
        time.sleep(0.1)
        rclpy.spin_once(self, timeout_sec=0.05)
        
        return False