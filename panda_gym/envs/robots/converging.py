import numpy as np
from gymnasium import spaces

from panda_gym.envs.core import PyBulletRobot
from panda_gym.assets import get_data_path
import os
import time


class Converging(PyBulletRobot):
    """My robot"""

    def __init__(self, sim, control_type="joints", **kwargs):
        super().__init__(
            sim,
            body_name="my_robot",  # choose the name you want
            file_name=os.path.join(get_data_path(), 'converging.urdf'),  # the path of the URDF file
            base_position=np.array([-.6, -.2, 0]),  # the position of the base
            action_space=None,
            joint_indices=None,  # list of the indices, as defined in the URDF
            joint_forces=None,  # force applied when robot is controled (Nm)
        )

        model_id = sim._bodies_idx["my_robot"]
        p = sim.physics_client
        infos = [p.getJointInfo(model_id, _id) for _id in range(p.getNumJoints(model_id))]
        self.joint_indices = np.array([info[0] for info in infos if info[2] == p.JOINT_REVOLUTE])
        self.action_space = spaces.Box(-1.0, 1.0, shape=(len(self.joint_indices),), dtype=np.float32)

        # https://www.universal-robots.com/articles/ur/robot-care-maintenance/max-joint-torques-cb3-and-e-series/
        joint_torque_by_size = [12, 28, 56, 150, 330]
        self.joint_forces = np.array([joint_torque_by_size[size] for size in [4, 4, 3, 2, 2, 2]])

        self.ee_link = next(info[0] for info in infos if info[12].decode("UTF-8") == "mirka_tool0")
        self.control_type = control_type
        self.reset()
        print(self.ee_link)

    def set_action(self, action: np.ndarray):
        action = action.copy()  # ensure action don't change
        action = np.clip(action, self.action_space.low, self.action_space.high)
        if self.control_type == "ee":
            ee_displacement = action[:3]
            target_arm_angles = self.ee_displacement_to_target_arm_angles(ee_displacement)
        else:
            arm_joint_ctrl = action[:6]
            target_arm_angles = self.arm_joint_ctrl_to_target_arm_angles(arm_joint_ctrl)

        self.control_joints(target_angles=target_arm_angles)

    def ee_displacement_to_target_arm_angles(self, ee_displacement: np.ndarray) -> np.ndarray:
        """Compute the target arm angles from the end-effector displacement.

        Args:
            ee_displacement (np.ndarray): End-effector displacement, as (dx, dy, dy).

        Returns:
            np.ndarray: Target arm angles, as the angles of the 7 arm joints.
        """
        ee_displacement = ee_displacement[:3] * 0.01  # limit maximum change in position
        # get the current position and the target position
        ee_position = self.get_ee_position()
        target_ee_position = ee_position + ee_displacement
        # Clip the height target. For some reason, it has a great impact on learning
        target_ee_position[2] = np.max((0, target_ee_position[2]))
        # compute the new joint angles
        target_arm_angles = self.inverse_kinematics(
            link=self.ee_link, position=target_ee_position, orientation=np.array([1.0, 0.0, 0.0, 0.0])
        )
        target_arm_angles = target_arm_angles[:7]  # remove fingers angles
        return target_arm_angles

    def arm_joint_ctrl_to_target_arm_angles(self, arm_joint_ctrl: np.ndarray) -> np.ndarray:
        return self.get_joint_angles() + arm_joint_ctrl * 0.05

    def get_ee_position(self) -> np.ndarray:
        """Returns the position of the end-effector as (x, y, z)"""
        return self.get_link_position(self.ee_link)

    def get_ee_velocity(self) -> np.ndarray:
        """Returns the velocity of the end-effector as (vx, vy, vz)"""
        return self.get_link_velocity(self.ee_link)

    def get_joint_angles(self) -> np.ndarray:
        """Returns the joint angles as (q1, q2, ..., qn)"""
        return [self.get_joint_angle(joint_index) for joint_index in self.joint_indices]

    def get_obs(self):
        # end-effector position and velocity
        return np.concatenate((
            np.array(self.get_joint_angles()),
            np.array(self.get_ee_position()),
            np.array(self.get_ee_velocity())
        ))

    def reset(self):
        neutral_angle = np.array([-3.141592, -1.745329, 2.0943957, -2.4434604, 1.570796, -1.570796])
        self.set_joint_angles(angles=neutral_angle + np.random.rand(6) * 0.1)


if __name__ == "__main__":
    from panda_gym.pybullet import PyBullet

    sim = PyBullet(render_mode="human")
    robot = Converging(sim)

    for i in range(50):
        if i < 15:
            robot.set_action(np.ones(6))
        else:
            robot.set_action(np.zeros(6))
        sim.step()
        print(robot.get_obs())
        time.sleep(0.1)
