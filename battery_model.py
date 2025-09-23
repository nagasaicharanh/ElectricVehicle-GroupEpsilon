# battery_model.py

import numpy as np

class BatteryModel:
    """
    Simple LFP battery model:
    - SOC state, power flow, regen efficiency, internal resistance
    - Voltage is clamped between Vmin and Vmax
    """
    def __init__(self, capacity_Wh, v_nominal=400, v_min=320, v_max=440, r_int_ohm=0.10,
                 soc_min=0.05, soc_max=0.95, regen_eff=0.70):
        self.capacity_Wh = capacity_Wh
        self.soc = soc_max  # start full by default (usable)
        self.v_nominal = v_nominal
        self.v_min = v_min
        self.v_max = v_max
        self.r_int = r_int_ohm
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.regen_eff = regen_eff

    @property
    def usable_Wh(self):
        return self.capacity_Wh * (self.soc_max - self.soc_min)

    def clamp_voltage(self, v):
        return np.clip(v, self.v_min, self.v_max)

    def step(self, p_batt_W, dt_s):
        """
        Advance SOC by dt based on battery power.
        p_batt_W > 0: discharge
        p_batt_W < 0: charge (regen)
        Returns net energy used (Wh, positive when discharging).
        """
        # Apply regen efficiency for charging
        p_effective = p_batt_W if p_batt_W >= 0 else p_batt_W * self.regen_eff

        # Energy in Wh over dt
        e_Wh = p_effective * dt_s / 3600.0

        # SOC update: positive e_Wh reduces SOC
        delta_soc = e_Wh / self.capacity_Wh
        self.soc = np.clip(self.soc - delta_soc, self.soc_min, self.soc_max)
        return max(e_Wh, 0.0)  # return energy drawn from pack as positive Wh

    def remaining_range_km_estimate(self, avg_consumption_Wh_per_km):
        energy_left_Wh = (self.soc - self.soc_min) * self.capacity_Wh
        if avg_consumption_Wh_per_km <= 0:
            return np.inf
        return energy_left_Wh / avg_consumption_Wh_per_km
