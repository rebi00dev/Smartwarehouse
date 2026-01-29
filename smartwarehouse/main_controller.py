import threading
import time
import rclpy
from rclpy.node import Node
import DR_init
import os, yaml
import numpy as np

from std_msgs.msg import String
from ament_index_python.packages import get_package_share_directory

from .gripper_controller import GripperController
from .pick2conveyor import PickAction
from .place2shelf import PlaceAction
from .move_home import MoveHomeAction
from .yolo import YoloDetectAction
from .waypoint import WaypointAction

POSE_PATH = os.path.join(
    get_package_share_directory("smartwarehouse"),
    "config",
    "pose.yaml"
)

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

ON, OFF = 1, 0
#===================================================================================================
# call yaml
def load_yaml(POSE_PATH):
    with open(POSE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

# ===================================================================================================
# action setting
def action_build(node, DR, poses):
    return {'pick':lambda target_pose: PickAction(node, dr=DR, poses=poses['Pick'], target_pose=target_pose),
            'place':lambda object, dict: PlaceAction(node, dr=DR, poses=poses['Place'], ingredient=object, dict=dict),
            'home':lambda : MoveHomeAction(node, dr=DR, poses=poses['Home']),
            'yolo':lambda : YoloDetectAction(node, dr=DR),
            'waypoint':lambda : WaypointAction(node, dr=DR, poses=poses['Waypoint']),
            }
# ===================================================================================================
#main
def main():
    rclpy.init()
    node = rclpy.create_node("main_controller", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    
    try:
        import DSR_ROBOT2 as DR
    except Exception as e:
        node.get_logger().error(f"초기화 중 오류 발생: {e}")
        raise
    #=================================================================
    # # 툴베이스 설정 ###############################################################변경 필요
    DR.set_robot_mode(0)

    # DR.set_tool("Tool Weight v2")
    # DR.set_tcp("GripperDA_v2")
    # DR.set_ref_coord(DR.DR_BASE)

    DR.set_robot_mode(1)

    #===================================================================================================
    # shelf objects dictionary
    dictonary = {
            'floor_1':0,
            'floor_2':0,
            'floor_3':0,
            'floor_4':0
            }
    
    # 데이터 및 코드 불러오기 =================================================================
    try:
        poses = load_yaml(POSE_PATH)
        actions_build = action_build(node,DR,poses)
    except:
        raise SyntaxError('pose.yaml,action build')
    
    
    # 반복 시작 ====================================================================
    while True:
        try:
            # Home 위치 이동 ========================================================
            actions_build['home']().execute()
            node.get_logger().info("Home 위치 도달. 물체 인식을 시작합니다.")

            # Yolo data 확인 =======================================================
            target_name, target_pose = actions_build['yolo']().execute()
            if not target_name:
                node.get_logger().info("감지된 물체가 없습니다. 재시도 중...")
                time.sleep(5)
                continue
            node.get_logger().info(f"타겟 감지: {target_name}")

            # pick ================================================================= 
            pick_success = actions_build['pick'](target_pose).execute()
            if not pick_success:
                node.get_logger().error("물체를 잡는 데 실패했습니다. 처음으로 돌아갑니다.")
                continue
            node.get_logger().info(f"{target_name} pick 완료. home 위치 이동")

            # home =================================================================
            actions_build['home']().execute()
            node.get_logger().info("이동 완료. waypoint 이동 ")

            # waypoint =============================================================
            actions_build['waypoint']().execute()
            node.get_logger().info("이동 완료. place 시작")

            # place ================================================================
            actions_build['place'](target_name).execute()
            node.get_logger().info(f"{target_name} place 완료. waypoint 이동.")

            # waypoint =============================================================
            actions_build['waypoint']().execute()
            node.get_logger().info(f"{target_name} 이동 완료. home 위치 이동")

        except Exception as e:
            node.get_logger().error(f"실행 중 예외 발생: {e}")
            actions_build['home']().execute()
            time.sleep(2)

if __name__ == "__main__":
    main()