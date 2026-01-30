import time
import DR_init
import time
from .base_action import BaseAction
from .gripper_controller import GripperController


VELOCITY, ACCURACY = 80, 60

class PlaceAction(BaseAction):
    def __init__(self, node, dr, poses, target_name):
        DR_init.__dsr__node = node
        self.node = node
        self.DR = dr
        self.place_pose = poses['place']
        self.target_pose = poses[target_name]

        self.gripper = GripperController()

    # 실행되는 동작
    def execute(self):

        # 놓는 위치 준비자세
        self.DR.movel(self.place_pose, vel=VELOCITY, acc=ACCURACY)
        time.sleep(0.5)

        # 놓을 위치로 접근
        approach_pose = list(self.target_pose)
        approach_pose[0] -= 50.0 
        approach_pose[2] += 10.0
        self.DR.movel(approach_pose, vel=VELOCITY, acc=ACCURACY)

        # 잡기 위치로 이동
        self.DR.movel(self.target_pose, vel=VELOCITY/2, acc=ACCURACY/2)

        #그리퍼 열기
        self.gripper.open()
        time.sleep(1.0)

        # 뒤로 빼기
        retract_pose = list(self.target_pose)
        retract_pose[0] -= 50.0
        retract_pose[2] += 10.0
        self.DR.movel(retract_pose, vel=VELOCITY, acc=ACCURACY)

        return 
         
