import DR_init
from .base_action import BaseAction

VELOCITY, ACCURACY = 80, 60

class WaypointAction(BaseAction):
    def __init__(self, node, dr, poses):
        self.DR = dr
        self.waypoint_pose = poses['waypoint']
        self.node = node


    # 실행되는 동작
    def execute(self):
        # home 위치로 로봇팔 이동
        self.DR.movej(self.waypoint_pose, vel = VELOCITY, acc=ACCURACY)


