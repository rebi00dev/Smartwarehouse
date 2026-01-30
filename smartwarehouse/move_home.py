import DR_init
from .base_action import BaseAction

VELOCITY, ACCURACY = 80, 60

class MoveHomeAction(BaseAction):
    def __init__(self, node, dr, poses):

        self.DR = dr
        self.home_pose = poses['home']
        self.node = node

    # 실행되는 동작
    def execute(self):
        # home 위치로 로봇팔 이동
        self.DR.movej(self.home_pose, vel = VELOCITY, acc=ACCURACY)
        print(self.home_pose)

