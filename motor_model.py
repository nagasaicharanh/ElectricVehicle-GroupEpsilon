# motor_model.py

import numpy as np

class MotorModel:
    """
    Simplified single-motor model:
    - Constant torque up to base speed
    - Constant power region after base speed
    - Efficiency map placeholder (scalar efficiency for now)
    """
    def __init__(self, torque_max_Nm, power_max_W, wheel_radius_m, peak_eff=0.92):
        self.torque_max = torque_max_Nm
        self.power_max = power_max_W
        self.wheel_radius = wheel_radius_m
        self.peak_eff = peak_eff
        self.base_speed_rad_per_s = self.power_max / max(self.torque_max, 1e-6)

    def available_torque_Nm(self, motor_speed_rad_per_s):
        motor_speed_rad_per_s = np.maximum(motor_speed_rad_per_s, 1e-3)
        torque = np.where(motor_speed_rad_per_s <= self.base_speed_rad_per_s,
                          self.torque_max,
                          self.power_max / motor_speed_rad_per_s)
        return torque

    def wheel_torque_from_motor(self, vehicle_speed_m_per_s, drivetrain_eff=0.90):
        motor_speed = vehicle_speed_m_per_s / max(self.wheel_radius, 1e-6)
        motor_torque = self.available_torque_Nm(motor_speed)
        wheel_torque = motor_torque * drivetrain_eff  # assuming 1:1 overall gear for simplicity
        return wheel_torque

    def motor_efficiency(self, power_W, speed_rad_per_s):
        # Placeholder: constant near-peak; you can replace with a 2D map later
        return self.peak_eff * np.ones_like(np.array(power_W, ndmin=1))
