import numpy as np
import sys
import carb

from isaacsim.examples.interactive.base_sample import BaseSample

from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.objects import DynamicCuboid

import isaacsim.robot_motion.motion_generation as mg
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.prims import SingleArticulation


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
        self.background_usd = "/home/rokey/IsaacSim-ros_workspaces/humble_ws/src/smartwarehouse/USD/smartwarehouse.usd"
        add_reference_to_stage(usd_path=self.background_usd, prim_path="/World")  
    

        return

    async def setup_post_load(self):
       
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)

        await self._world.play_async()
        self.task_phase = 1
        return

    def physics_step(self, step_size):
        return