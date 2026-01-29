import rclpy
import time
from .creat_tcp import TcpManager

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
        
        set_robot_mode(0)
        
        setup = TcpManager(node)
        time.sleep(2)
        # TCP 설정 실행
        setup.set_new_tcp('tcp1', [0.0, 0.0, 220.0, 0.0, 180.0, 0.0])
        set_tcp('tcp1')
        time.sleep(2)
        set_robot_mode(1)
        time.sleep(1.0)
        set_velx(30, 20)    # set global task speed : 30(mm/sec), 20(deg/sec)
        set_accx(60, 40)    # set global task speed : 60(mm/sec2), 40(deg/sec2)

        velx = [50, 50]
        accx = [100, 100]

        p1= posj(0.0, 0.0, 90.0, 0.0, 90.0, 0.0) #joint

        # x1= posx(368.000, 6.250, 425.000, 45.000, 180.000, 45.000)#task
        # x1= posx(250.000, 250.000, 250.000, 45.000, 180.000, 45.000)#task
        while rclpy.ok():

            # print(movej(p1, vel=100, acc=100))
            print(get_current_posx()[0])
            print(get_current_posj())
            print(movej(p1, vel=100, acc=100))
            time.sleep(5)
        rclpy.shutdown()

if __name__ == "__main__":
        main()
