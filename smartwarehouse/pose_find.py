import rclpy
import time
from .creat_tcp import TcpManager
from .gripper_controller import GripperController
# for single robot
ROBOT_ID   = "dsr01"
ROBOT_MODEL= "m0609"

import DR_init
DR_init.__dsr__id   = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


def main(args=None):
        rclpy.init(args=args)

        node = rclpy.create_node('single_robot_simple_py', namespace=ROBOT_ID)

        DR_init.__dsr__node = node

        try:
                from DSR_ROBOT2 import movej,movel, set_velx, set_accx, get_current_posx, get_current_posj, set_tcp, set_robot_mode
                from DSR_ROBOT2 import posj, posx
        except ImportError as e:
                print(f"Error importing DSR_ROBOT2 : {e}")
                return
        
        # TCP 설정 실행 =====================================================================================
        set_robot_mode(0)
        
        setup = TcpManager(node)
        time.sleep(2)
        
        setup.set_new_tcp('tcp1', [0.0, 0.0, 220.0, 0.0, 180.0, 0.0])
        set_tcp('tcp1')
        time.sleep(2)
        set_robot_mode(1)
        time.sleep(1.0)
        # ==================================================================================================
        set_velx(30, 20)    # set global task speed : 30(mm/sec), 20(deg/sec)
        set_accx(60, 40)    # set global task speed : 60(mm/sec2), 40(deg/sec2)

        velx = [50, 50]
        accx = [100, 100]
        # home      task: [368.000, 6.250, 205.000, 180.000, 0.000, -180.000]
        #           joint: [0.0, 0.0, 90.0, 0.0, 90.0, 0.0]

        # waypoint  task: [-6.250, 500.00, 205.00, 90.000, -45.000, 0.000]
        #           joint: [90.000, -13.862, 117.682, -0.000, 31.180, 0.000]

        # pick      task: [500.000, 6.250, 205.000, 0.000, -45.000, 0.000]
        
        # clock(3)  task: [480.939, 56.106, 120.048, 00.000, -45.000, 0.000] x, z만 움직여서 위치 지정 후 y,z값으로 놓기
        # dice(2)   task: [-6.250, 500.00, 205.00, 00.000, -45.000, 0.000]
        # lemon(1)  task: [-6.250, 500.00, 205.00, 00.000, -45.000, 0.000]

        home = posj(0.0, 0.0, 90.0, 0.0, 90.0, 0.0) #joint
        gripper = GripperController()
        phase = 1
        movej(home, vel=100, acc=100)
        while rclpy.ok():
            # x= posx(500.000, 6.250, 205.000, 0.000, -45.000, 0.000)
            # print(f'posx: {get_current_posx()[0]}')
            # print(f'target : {x}')
            # movel(x, velx, accx)
            
            # p = posj(90.000, -13.862, 117.682, -0.000, 31.180, 0.000) #joint
            # print(f'posj: {get_current_posj()}')
            # print(f'target : {p}')
            # movej(p, vel=100, acc=100)

            pick_pose = posx(500.000, 6.250, 205.000, 0.000, -45.000, 0.000)
            pick_approch = posx(480.939, 46.106, 220.048, 0.000, -45.000, 0.000)
            pick_clock= posx(480.939, 46.106, 120.048, 0.000, -45.000, 0.000)
            waypoint = posx(-6.250, 500.00, 205.00, 90.000, -45.000, 0.000)

            # 그리퍼동작
        #     if phase == 1:
        #         if gripper.reached or gripper.grasp:
        #             phase = 2
        #             continue
        #         gripper.close()
                
                       
        #     if phase == 2:
        #         if gripper.reached:
        #             phase = 1
        #             continue
        #         gripper.open()
            print('2')
            movej(home, vel=100, acc=100)
            time.sleep(5)
            print('3')
            movel(pick_pose, velx, accx)
            gripper.reached = False
            while phase == 1:
                if gripper.reached:
                    phase = 2
                    break
                gripper.open()
            time.sleep(5)
            print('4')
            movel(pick_approch, velx, accx)
            time.sleep(5)
            print('5')
            movel(pick_clock, velx, accx)
            # 그리퍼동작
            gripper.reached = False
            while phase == 2:
                if gripper.reached or gripper.grasp:
                    phase = 1
                    break
                gripper.close()
            time.sleep(5)
            print('6')
            gripper.close()
            time.sleep(5)
            print('7')
            movel(pick_approch, velx, accx)
            time.sleep(5)
            print('8')
            movel(waypoint, velx, accx)
            time.sleep(5)
        #     break
        rclpy.shutdown()

if __name__ == "__main__":
        main()
