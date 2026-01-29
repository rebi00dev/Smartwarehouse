import DR_init
from .base_action import BaseAction

VELOCITY, ACCURACY = 80, 60

class MoveHomeAction(BaseAction):
    def __init__(self, node, DR, poses):
        DR_init.__dsr__node = node

        self.DR = DR
        self.hom_pose_pose = poses['waypoint']
        self.node = node


    # 실행되는 동작
    def execute(self):
        # home 위치로 로봇팔 이동
        self.DR.movej(self.home_pose, vel = VELOCITY, acc=ACCURACY)


