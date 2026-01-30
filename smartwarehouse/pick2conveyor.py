import time
import DR_init
import time
from .base_action import BaseAction
from .gripper_controller import GripperController


VELOCITY, ACCURACY = 80, 60
DR = None


class PickAction(BaseAction):
    def __init__(self, node, dr, poses, target_pose):
        self.node = node
        self.DR = dr
        self.pick_pose = poses['pick']
        self.target_pose = target_pose

        self.max_retry = 3
        self.success = False


        self.gripper = GripperController()

    # 실행되는 동작
    def execute(self):

        # 그리퍼를 열고 대기 포즈로 이동
        self.gripper.reached = False
        while not self.gripper.reached:
                if self.gripper.reached:
                    break
                self.gripper.open()
        self.DR.movel(self.pick_pose, vel=VELOCITY, acc=ACCURACY)
        time.sleep(0.5)

        # 물체 위로 접근
        approach_pose = list(self.target_pose)
        approach_pose[2] += 50.0  
        self.DR.movel(approach_pose, vel=VELOCITY, acc=ACCURACY)

        # 잡기 위치로 하강
        self.DR.movel(self.target_pose, vel=VELOCITY/2, acc=ACCURACY/2)

        #그리퍼 닫기
        self.gripper.reached = False
        while not self.gripper.reached:
                if self.gripper.reached:
                    break
                self.gripper.close()
        time.sleep(1.0)

        retract_pose = list(self.target_pose)
        retract_pose[2] += 100.0
        self.DR.movel(retract_pose, vel=VELOCITY, acc=ACCURACY)

        return self.success
         
