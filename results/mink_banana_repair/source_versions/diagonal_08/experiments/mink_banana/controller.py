"""Keep the actual two-pad center fixed while closing, using only proprioception."""
import numpy as np
from scipy.spatial.transform import Rotation
from experiments.mink_wholebody.controller import GraspController as BaseController

class GraspController(BaseController):
    def __init__(self,config,ik,mode='grasp'):
        super().__init__(config,ik,mode)
        self.nominal_rotation=self.ee_rotation.copy()
    def step(self,p):
        if self.cfg.get('pinch_mode')=='fixed_tip':
            result=super().step(p)
            if self.state=='APPROACH' and self.age>=float(self.cfg.get('early_close_after_s',1e9)):
                self.target[18]=0.;result[18]=0.
            return result
        q=np.asarray(p['joint_pos']).reshape(19)
        center,alpha,moving=self.ik.update_pinch_frame(q)
        self.cfg['tcp_offset_link06']=center.tolist()
        beta=0.
        if self.state in ['LIFT','HOLD','DONE']:
            fraction=min(self.age/float(self.cfg.get('lift_tilt_duration_s',3.)),1.) if self.state=='LIFT' else 1.
            beta=np.deg2rad(float(self.cfg.get('lift_tilt_deg',0.)))*fraction
        self.ee_rotation=self.nominal_rotation@Rotation.from_euler('y',alpha-beta).as_matrix()
        result=super().step(p)
        self.last_ik.update(actual_gripper_angle=float(q[-1]),pinch_center_link06=center.tolist(),pad_leveling_angle_rad=alpha,fixed_pad_link06=self.ik.fixed_pad.tolist(),moving_pad_link06=moving.tolist())
        return result
