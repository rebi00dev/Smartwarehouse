import os
import time
import sys
from scipy.spatial.transform import Rotation
import rclpy
import numpy as np
import DR_init
import time
from .base_action import BaseAction
from .gripper_controller import GripperController


from od_msg.srv import SrvDepthPosition
from std_srvs.srv import Trigger
from ament_index_python.packages import get_package_share_directory

package_path = get_package_share_directory("co_cocktail_robot")

DEPTH_OFFSET = -5.0
MIN_DEPTH = 2.0

VELOCITY, ACCURACY = 80, 60
DR = None


class PickAction(BaseAction):
    def __init__(self, node, DR, poses, object):
        DR_init.__dsr__node = node
        self.DR = DR
        self.pick_pose = poses
        self.object = object
        self.node = node

        self.max_retry = 3
        self.success = False


        self.get_position_client = node.create_client(SrvDepthPosition, "/depth")
        while not self.get_position_client.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Waiting for get_depth_position service...")
        self.get_position_request = SrvDepthPosition.Request()

        self.gripper = GripperController()

    # 실행되는 동작
    def execute(self):
        
        self.gripper.open()
        time.sleep(1)

        # 거리 계산 (음료와 가니쉬일 경우)
            
            self.get_position_request.target = self.object
            self.get_logger().info(f"Requesting 3D position for {self.object}")
            depth_future = self.get_position_client.call_async(self.get_position_request)
            rclpy.spin_until_future_complete(self.node, depth_future)

            if depth_future.result():
                pos = depth_future.result().depth_position.tolist()
                self.get_logger().info(f"Object {self.object} detected at {pos}")

                gripper2cam_path = os.path.join(package_path, "resource", "T_gripper2camera.npy")
                robot_posx = self.DR.get_current_posx()[0]
                td_coord = self.transform_to_base(pos, gripper2cam_path, robot_posx)

                if self.object in BEVERAGE_SET: 
                    if td_coord[1] and sum(td_coord) != 0:
                                            td_coord[1] -= 40  # DEPTH_OFFSET
                                        # td_coord[1] = max(td_coord[1], 2)  # MIN_DEPTH: float = 2.0
                elif self.object in GARNISH_SET:
                    if self.object == 'lime':
                        if td_coord[2] and sum(td_coord) != 0:
                                            td_coord[2] -= 12  # DEPTH_OFFSET
                    elif self.object == 'cherry':
                        if td_coord[2] and sum(td_coord) != 0:
                                            td_coord[2] -= 5


                # 계산된 결과
                target_pos = list(td_coord[:3]) + robot_posx[3:]
                grap_pos = target_pos.copy()
                apporach_pos = target_pos.copy()
                apporach_pos[2] = target_pos[2] + 30

                # Detect 위치로 이동
                self.DR.movel(target_pos, vel=VELOCITY, acc=ACCURACY)
                # self.DR.movel(grap_pos, vel=VELOCITY, acc=ACCURACY)
                # self.DR.movel(grap_pos, vel=VELOCITY, acc=ACCURACY)
                self.DR.mwait()

                # 그리퍼 닫기(close_gripper)
                self.gripper.close()
                
                # 예외처리 체크
                status = self.gripper.get_status()
                if status[1]:  # grip detected
                    self.success = True
                    break
                else:
                    self.gripper.move_gripper(1100, force_val=200)
                    self.get_logger().warn(f"Grip not detected (attempt {attempt+1}), retrying...")


            # 뒤로 이동
            self.DR.movel(apporach_pos, vel=VELOCITY, acc=ACCURACY)
            if self.object in BEVERAGE_SET:
                self.DR.movel(apporach_pos, vel=VELOCITY, acc=ACCURACY)
                self.DR.movel(self.pick_pose["beverage_detect"]["task"], vel=VELOCITY, acc=ACCURACY)
            elif self.object in GARNISH_SET:
                self.DR.movel(self.pick_pose["garnish_detect"]["task"], vel=VELOCITY, acc=ACCURACY)

            if attempt == 3:
                raise KeyError


    def get_robot_pose_matrix(self, x, y, z, rx, ry, rz):
        R = Rotation.from_euler("ZYZ", [rx, ry, rz], degrees=True).as_matrix()
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = [x, y, z]
        return T
    

    def get_target_pos(self, target):
        self.get_position_request.target = target
        self.get_logger().info("call depth position service with object_detection node")
        get_position_future = self.get_position_client.call_async(
            self.get_position_request
        )
        rclpy.spin_until_future_complete(self.node, get_position_future)

        if get_position_future.result():
            result = get_position_future.result().depth_position.tolist()
            self.get_logger().info(f"Received depth position: {result}")
            if sum(result) == 0:
                self.get_logger().warn("No target position")
                return None

            gripper2cam_path = os.path.join(
                package_path, "resource", "T_gripper2camera.npy"
            )
            robot_posx = self.DR.get_current_posx()[0]
            td_coord = self.transform_to_base(result, gripper2cam_path, robot_posx)

            if td_coord[2] and sum(td_coord) == 0:
                raise KeyError

            if td_coord[2] and sum(td_coord) != 0:
                td_coord[2] += DEPTH_OFFSET  # DEPTH_OFFSET
                td_coord[2] = max(td_coord[2], MIN_DEPTH)  # MIN_DEPTH: float = 2.0

            target_pos = list(td_coord[:3]) + robot_posx[3:]
            return target_pos
        return None


    def transform_to_base(self, camera_coords, gripper2cam_path, robot_pos):
        """
        Converts 3D coordinates from the camera coordinate system
        to the robot's base coordinate system.
        """
        gripper2cam = np.load(gripper2cam_path)
        coord = np.append(np.array(camera_coords), 1)  # Homogeneous coordinate

        x, y, z, rx, ry, rz = robot_pos
        base2gripper = self.get_robot_pose_matrix(x, y, z, rx, ry, rz)

        # 좌표 변환 (그리퍼 → 베이스)
        base2cam = base2gripper @ gripper2cam
        td_coord = np.dot(base2cam, coord)

        return td_coord[:3]