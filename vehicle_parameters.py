# vehicle_parameters.py

import math

class BYD_SEAL_Premium_Params:
    """
    Official specs from uploaded sheet + red-marked assumptions for missing data.
    """
    def __init__(self):
        # Official specifications
        self.variant = "BYD SEAL Premium (RWD)"
        self.mass_kg = 2055          # 🔴 estimated kerb mass (Premium variant)
        self.cd = 0.219              # aerodynamic drag coefficient (official)
        self.frontal_area_m2 = 2.74  # 🔴 derived: 0.85 * width * height
        self.motor_power_max_W = 230_000  # 230 kW (official)
        self.motor_torque_max_Nm = 360    # 360 Nm (official)
        self.top_speed_kmh = 180          # (official)
        self.battery_capacity_Wh = 82_560 # 82.56 kWh (official usable)
        self.tire_size = "235/45 R19"     # (official)
        self.wheel_radius_m = 0.332       # 🔴 derived from tire size
        self.wltp_range_km = 570          # (official)
        self.wltp_energy_kWh_per_100km = 16.6  # (official)
        self.dc_charge_30_80_min = 32     # (official)
        self.dc_power_kW = 150            # (official)
        self.ac_power_kW = 7              # (official)

        # Physical constants (assumed)
        self.air_density_kg_per_m3 = 1.225   # 🔴 standard atmosphere (15C, sea level)
        self.g_m_per_s2 = 9.81               # gravity

        # Efficiency/loss assumptions (red-marked)
        self.motor_peak_eff = 0.92           # 🔴 PM motor
        self.drivetrain_eff = 0.90           # 🔴 inverter + gearbox
        self.aux_power_W = 1400              # 🔴 HVAC, electronics (avg)
        self.regen_eff = 0.70                # 🔴 regen round-trip efficiency

        # Rolling resistance model (red-marked)
        # Base rolling resistance + weak speed dependency
        self.mu_rr_base = 0.011              # 🔴 for 235/45 R19 low-RR EV tires
        self.mu_rr_k = 1.5e-5                # 🔴 speed^2 coefficient (mks with v in m/s)

        # Battery operating window assumptions (red-marked)
        self.v_nominal_V = 400               # 🔴 pack nominal voltage
        self.v_max_V = 440                   # 🔴 at high SOC
        self.v_min_V = 320                   # 🔴 low SOC limit
        self.r_int_ohm = 0.10                # 🔴 lumped internal resistance
        self.soc_min = 0.05                  # 🔴 reserve
        self.soc_max = 0.95                  # 🔴 top buffer

        # Speed limits
        self.max_speed_kmh_official = 180    # official cap

    def summary(self):
        return {
            "variant": self.variant,
            "mass_kg": self.mass_kg,
            "cd": self.cd,
            "frontal_area_m2": self.frontal_area_m2,
            "motor_power_max_W": self.motor_power_max_W,
            "motor_torque_max_Nm": self.motor_torque_max_Nm,
            "top_speed_kmh": self.top_speed_kmh,
            "battery_capacity_Wh": self.battery_capacity_Wh,
        }
