"""Keep the actual two-pad center fixed while closing, using only proprioception."""
import numpy as np
from scipy.spatial.transform import Rotation
from experiments.mink_wholebody.controller import GraspController as BaseController

class GraspController(BaseController):
    def __init__(self,config,ik,mode='grasp'):
        super().__init__(config,ik,mode)
        self.nominal_rotation=self.ee_rotation.copy()
    def step(self,p):
        q=np.asarray(p['joint_pos']).reshape(19)
        center,alpha,moving=self.ik.update_pinch_frame(q)
        self.cfg['tcp_offset_link06']=center.tolist()
        self.ee_rotation=self.nominal_rotation@Rotation.from_euler('y',alpha).as_matrix()
        result=super().step(p)
        self.last_ik.update(actual_gripper_angle=float(q[-1]),pinch_center_link06=center.tolist(),pad_leveling_angle_rad=alpha,fixed_pad_link06=self.ik.fixed_pad.tolist(),moving_pad_link06=moving.tolist())
        return result
