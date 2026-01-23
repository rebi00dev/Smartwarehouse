import numpy as np
import sys
import carb

from isaacsim.examples.interactive.base_sample import BaseSample

from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.objects import DynamicCuboid

import isaacsim.robot_motion.motion_generation as mg
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.prims import SingleArticulation


# class RMPFlowController(mg.MotionPolicyController):

#     def __init__(
#         self,
#         name: str,
#         robot_articulation: SingleArticulation,
#         physics_dt: float = 1.0 / 60.0
#     ) -> None:

#         self.articulation_rmp = mg.ArticulationMotionPolicy(robot_articulation, self.rmp_flow, physics_dt)

#         mg.MotionPolicyController.__init__(self, name=name, articulation_motion_policy=self.articulation_rmp)
#         (
#             self._default_position,
#             self._default_orientation,
#         ) = self._articulation_motion_policy._robot_articulation.get_world_pose()
#         self._motion_policy.set_robot_base_pose(
#             robot_position=self._default_position, robot_orientation=self._default_orientation
#         )
#         return

#     def reset(self):
#         mg.MotionPolicyController.reset(self)
#         self._motion_policy.set_robot_base_pose(
#             robot_position=self._default_position, robot_orientation=self._default_orientation
#         )

class Smartwarehouse(BaseSample):
    def __init__(self) -> None:
        super().__init__()

        self.BROWN = np.array([0.5, 0.2, 0.1])
        self._brown_cube_position = np.array([-1.5, 0.0, 0.5])
        self.task_phase = 1
        self._wait_counter = 0
        self.robot_position = np.array([1.0, 0.0, 0.0])
        self.place_position = np.array([1.5, 0.5, 0.05])
        return

    
    def setup_scene(self):
        # world = self.get_world()
        self.background_usd = "/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/USD/smartwarehouse.usd"
        add_reference_to_stage(usd_path=self.background_usd, prim_path="/World")  
        
        # world.scene.add(DynamicCuboid(
        #     prim_path="/World/BrownCube", 
        #     name="brown_cube",
        #     position=self._brown_cube_position, 
        #     scale=np.array([0.05, 0.05, 0.05]), 
        #     color=self.BROWN
        # ))

        return

    async def setup_post_load(self):
        # self._world = self.get_world()

        # self.cube = self._world.scene.get_object("brown_cube")

        # self.cspace_controller=RMPFlowController(name="my_ur10_cspace_controller", robot_articulation=self.robots)
        
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)

        await self._world.play_async()
        self.task_phase = 1
        return

    def physics_step(self, step_size):
        return