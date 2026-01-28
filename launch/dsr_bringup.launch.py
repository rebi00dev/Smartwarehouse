from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression

from launch_ros.actions import Node
from launch.conditions import IfCondition
# 
#  dsr_bringup2
#  Author: Minsoo Song (minsoo.song@doosan.com)
#  
#  Copyright (c) 2024 Doosan Robotics
#  Use of this source code is governed by the BSD, see LICENSE
# 

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from dsr_bringup2.utils import read_update_rate, show_git_info

def print_launch_configuration_value(context, *args, **kwargs):
    # LaunchConfiguration 값을 평가합니다.
    gz_value = LaunchConfiguration('gz').perform(context)
    # 평가된 값을 콘솔에 출력합니다.
    print(f'LaunchConfiguration gz: {gz_value}')
    return gz_value

def generate_launch_description():
    ARGUMENTS =[ 
        DeclareLaunchArgument('name',  default_value = 'dsr01',     description = 'NAME_SPACE'     ),
        DeclareLaunchArgument('host',  default_value = '127.0.0.1', description = 'ROBOT_IP'       ),
        DeclareLaunchArgument('port',  default_value = '12345',     description = 'ROBOT_PORT'     ),
        DeclareLaunchArgument('mode',  default_value = 'virtual',   description = 'OPERATION MODE' ),
        DeclareLaunchArgument('model', default_value = 'm0609',     description = 'ROBOT_MODEL'    ),
        DeclareLaunchArgument('color', default_value = 'white',     description = 'ROBOT_COLOR'    )
    ]
    # gui = LaunchConfiguration("gui")
    mode = LaunchConfiguration("mode")
    
    update_rate = str(read_update_rate()) # get update_rate from yaml
    show_git_info() # print git info
    
    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("dsr_description2"),
                    "xacro",
                    LaunchConfiguration('model'),
                ]
            ),
            ".urdf.xacro",
            " name:=", LaunchConfiguration('name'),
            " host:=", LaunchConfiguration('host'),
            " port:=", LaunchConfiguration('port'),
            " mode:=", LaunchConfiguration('mode'),
            " model:=", LaunchConfiguration('model'),
            " update_rate:=", update_rate,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    robot_controllers = [
        PathJoinSubstitution([
            FindPackageShare("dsr_controller2"),
            "config",
            "dsr_update_rate.yaml",
        ]),
        PathJoinSubstitution([
            FindPackageShare("dsr_controller2"),
            "config",
            "dsr_controller2.yaml",
        ])
    ]
    
    run_emulator_node = Node(
        package="dsr_bringup2",
        executable="run_emulator",
        namespace=LaunchConfiguration('name'),
        parameters=[
            {"name":    LaunchConfiguration('name')  }, 
            {"rate":    100         },
            {"standby": 5000        },
            {"command": True        },
            {"host":    LaunchConfiguration('host')  },
            {"port":    LaunchConfiguration('port')  },
            {"mode":    LaunchConfiguration('mode')  },
            {"model":   LaunchConfiguration('model') },
            {"gripper": "none"      },
            {"mobile":  "none"      },
            #parameters_file_path       # 파라미터 설정을 동일이름으로 launch 파일과 yaml 파일에서 할 경우 yaml 파일로 셋팅된다.    
        ],
        condition=IfCondition(PythonExpression(["'", mode, "' == 'virtual'"])),
        output="screen",
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace=LaunchConfiguration('name'),
        parameters=[robot_description] + robot_controllers,
        output="both",
    )

    
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        namespace=LaunchConfiguration('name'),
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        namespace=LaunchConfiguration('name'),
        executable="spawner",
        arguments=["dsr_controller2", "-c", "controller_manager"],
    )
    
    
    nodes = [
        run_emulator_node,
        robot_controller_spawner,
        joint_state_broadcaster_spawner,
        control_node,
    ]

    return LaunchDescription(ARGUMENTS + nodes)
