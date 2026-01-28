import threading
import time
import rclpy
from rclpy.node import Node
import DR_init
import os, yaml
import numpy as np

from ament_index_python.packages import get_package_share_directory
from dsr_msgs2.srv import SetRobotMode
from cocktail_interfaces.srv import GetKeywordList

from .pick_and_place.onrobot import RG
from .pick_and_place.pick import PickAction
from .pick_and_place.take import TakeAction
from .pick_and_place.drop import DropAction
from .pick_and_place.pour import PourAction
from .pick_and_place.shake import ShakerAction
from .pick_and_place.open_close import TumblerAction
from .pick_and_place.head_tilt import HeadTiltAction
from .pick_and_place.head_nod import HeadNodAction


POSE_PATH = os.path.join(
    get_package_share_directory("co_cocktail_robot"),
    "pose.yaml"
)

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"
VELOCITY, ACC = 60, 60

GRIPPER_NAME = "rg2"
TOOLCHANGER_IP = "192.168.1.1"
TOOLCHANGER_PORT = "502"
gripper = RG(GRIPPER_NAME, TOOLCHANGER_IP, TOOLCHANGER_PORT)

ON, OFF = 1, 0
#===================================================================================================
# call yaml
def load_yaml(POSE_PATH):
    with open(POSE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data
#===================================================================================================
# pose.yaml check
def recursive_check(data_dict):
    if isinstance(data_dict, dict):
        for _, value in data_dict.items():
            recursive_check(value)
    elif isinstance(data_dict, list):
        if len(data_dict) == 6 and all(isinstance(v, (int, float)) for v in data_dict):
            arr = np.array(data_dict, dtype=np.float64)
            print(f"float64[6] OK: {arr}")
        elif len(data_dict) == 6:
            raise TypeError(f"6개인데 float/int 아님: {data_dict}")
        elif all(isinstance(v, (int, float)) for v in data_dict):
            raise IndexError(f"값 개수 오류 ({len(data_dict)}개): {data_dict}")
        else:
            raise TypeError(f"값 개수와 타입 모두 문제: {data_dict}")
#===================================================================================================
# call llm
def llm_cycle(trigger):
    get_keyword_client = trigger.create_client(GetKeywordList, "/get_keyword")
    while not get_keyword_client.wait_for_service(timeout_sec=3.0):
        trigger.get_logger().info("Waiting for get_keyword service...")
    get_keyword_request = GetKeywordList.Request()
    get_keyword_future = get_keyword_client.call_async(get_keyword_request)
    rclpy.spin_until_future_complete(trigger,get_keyword_future)
    return get_keyword_future.result().keywords

#===================================================================================================
#llm check
def llm_check(trigger,keyword_result):
    if keyword_result:
        for group in keyword_result:
            if len(list(group.items)) == 3:
                object,action,destination = group.items
                print(object,action,destination)
                if object is None or action is None or destination is None:
                    trigger.get_logger().warn('llm_check error')
                    raise NameError('keyword lost')
                elif object not in ['green-juice', 'red-juice', 'blue-juice', 'tequila', 'lime', 'cherry', 'shaker','X']:
                    trigger.get_logger().warn('llm_check error')
                    raise NameError('object not defined') 
                elif action not in ['pick', 'take', 'drop', 'pour', 'open', 'close', 'shake', 'head_nod']:
                    trigger.get_logger().warn('llm_check error')
                    raise NameError('action not defined')
                elif destination not in ['pos1', 'pos2', 'pos3_1','pos3_2','pos3_3','pos3_4','pos4','pos5','X']:
                    trigger.get_logger().warn('llm_check error')
                    raise NameError('destination not defined')
            else:
                trigger.get_logger().warn('lm_check error')
                raise IndexError('llm length error')
    else:
        trigger.get_logger().warn('llm_check error')
        raise ImportError('No result')
        
#===================================================================================================
# action setting
def action_build(node,poses):
    return {'pick':lambda object: PickAction(node, poses=poses['Pick'], ingredient=object),
            'take':lambda object, destination: TakeAction(node, poses=poses['Take'], ingredient=object,target=destination),
            'drop':lambda destination: DropAction(node, poses=poses['Drop'], target=destination),
            'pour':lambda destination, on_hand: PourAction(node, poses=poses['Pour'],target=destination, on_hand = on_hand),
            'open':lambda: TumblerAction(node, poses=poses['Tumbler'], move='open'),
            'close':lambda: TumblerAction(node, poses=poses['Tumbler'], move='close'),
            'shake':lambda: ShakerAction(node, poses=poses['Shaker']),
            'head_tilt':lambda: HeadTiltAction(node),
            'head_nod':lambda: HeadNodAction(node)
            }

#===================================================================================================
#check gripper 1
def double_check(trigger, on_hand):
    grasp = trigger.get_status()[1]
    if not grasp and on_hand == '':
        return False
    elif grasp and on_hand != '':
        return True
    else:
        raise ValueError('not match in gripper and dictionary')
#===================================================================================================
# 경유점
def course(move,poses,mv_type="task"):
    course = poses['home'][mv_type]
    move(course, vel=VELOCITY,acc=ACC)
# ===================================================================================================
#main
def main():
    rclpy.init()
    trigger = Node('Trigger_keyword')
    node = rclpy.create_node("main", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    
    try:
        from DSR_ROBOT2 import (
            movej,
            movel,
            set_tool,
            set_tcp,
            set_ref_coord,
            set_robot_mode,
            DR_BASE
        )

    except Exception as e:
        node.get_logger().error(f"초기화 중 오류 발생: {e}")
        raise
    #=================================================================
    # 툴베이스 설정
    set_robot_mode(0)

    set_tool("Tool Weight v2")
    set_tcp("GripperDA_v2")
    set_ref_coord(DR_BASE)

    set_robot_mode(1)
    #=================================================================
    # 데이터 및 코드 불러오기
    try:
        poses = load_yaml(POSE_PATH)
        recursive_check(poses)
        actions_build = action_build(node,poses)
    except:
        raise SyntaxError('pose.yaml,action build,llm_cycle')
    
    #===================================================================================================
    # surrounding objects
    surrounding_objects = {
                        'on_hand':'',
                        'shaker':'open'
                        }
    #====================================================================
    # 반복 시작
    while True:
        try:
            #=================================================================
            #llm 데이터 확인
            keyword_result = llm_cycle(node)
            llm_check(node,keyword_result=keyword_result)
            #=================================================================
            #경유점
            movej(poses['home']['joint'],vel=VELOCITY,acc=ACC)
            for group in keyword_result:
                object,action,destination = group.items
                course(movel,poses=poses) # home
                #gripper test
                gripper_status = gripper.get_status()
                if 1 in gripper_status[2:]:
                    node.get_logger().info(f'gripper error, {gripper_status}')
                    raise ValueError('gripper stoped')
                # double hand check
                hand_check = double_check(gripper,surrounding_objects['on_hand'])
                if surrounding_objects['on_hand'] == 'shaker':
                    hand_check = 1
                if action in ['take']:    
                    if hand_check:
                        node.get_logger().info(f'{surrounding_objects["on_hand"]} in gripper before {action}')
                        raise ValueError('hand check')
                    else:
                        actions_build[action](object, destination).execute()
                        if gripper.get_status()[1]:
                            surrounding_objects['on_hand'] = object
                        else:
                            node.get_logger().info(f'nothing in gripper after action')
                            raise ValueError(f'{action} error')              

                elif action in ['pick']:
                    if hand_check:
                        node.get_logger().info(f'{surrounding_objects["on_hand"]} in gripper before {action}')
                        raise ValueError('hand check')
                    else:
                        actions_build[action](object).execute()
                        if object != 'shaker':
                            if gripper.get_status()[1]:
                                surrounding_objects['on_hand'] = object
                            else:
                                node.get_logger().info(f'nothing in gripper after action')
                                raise ValueError(f'{action} error')
                        else:
                            surrounding_objects['on_hand'] = object

                elif action in ['open', 'close']:
                    if not hand_check:
                        if action == 'open' and surrounding_objects['shaker'] == 'open':
                            node.get_logger().info(f'{surrounding_objects["shaker"]} on hand, skip {action} action...')
                        elif action == 'close' and surrounding_objects['shaker'] == 'close':
                            node.get_logger().info(f'{surrounding_objects["shaker"]} on hand, skip {action} action...')
                        else:
                            actions_build[action]().execute()
                            surrounding_objects['shaker'] = action
                    else:
                        node.get_logger().info(f'nothing in gripper before {action}')
                        raise ValueError('hand check')

                elif action in ['pour']:
                    if hand_check:
                        actions_build[action](destination, surrounding_objects["on_hand"]).execute()
                    else:
                        node.get_logger().info(f'nothing on hand')
                        raise ValueError('hand check')

                elif action in ['drop']:
                    if hand_check:
                        actions_build[action](destination).execute()
                        if not gripper.get_status()[1]:
                            surrounding_objects['on_hand'] = ''
                        else:
                            node.get_logger().info(f'something in gripper after drop action')
                            raise ValueError(f'{action} error')    
                    else:
                        node.get_logger().info(f'nothing on hand, skip {action} action...')

                elif action in ['shake']:
                    if hand_check:
                        node.get_logger().info(f'something in gripper before action') 
                        raise ValueError('hand check')
                    else:
                        if surrounding_objects['shaker'] == 'open':
                            node.get_logger().info(f'{surrounding_objects["shaker"]} opened')
                            raise ValueError(f'{action} error')
                        else:
                            actions_build[action]().execute()
                elif action in ['head_nod']:
                    actions_build[action]().execute()
                else:
                    raise KeyError('error in action_list and on_hand')
            course(movel,poses,'task')
            course(movej,poses,'joint')
        except Exception as e:
            node.get_logger().error(f"실행 중 예외 발생: {e}")
            course(movel,poses,'task')
            course(movej,poses,'joint')
            actions_build['head_tilt']().execute()

if __name__ == "__main__":

    main()