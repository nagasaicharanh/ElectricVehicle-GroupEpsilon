# physics.py

import numpy as np

def rolling_resistance_force(velocity_m_per_s, mass_kg, g, mu_rr_base=0.011, mu_rr_k=1.5e-5):
    # speed-dependent rolling resistance, v in m/s
    mu_rr = mu_rr_base + mu_rr_k * velocity_m_per_s**2
    return mu_rr * mass_kg * g

def aero_drag_force(velocity_m_per_s, rho, cd, area_m2):
    return 0.5 * rho * cd * area_m2 * velocity_m_per_s**2

def gradient_force(mass_kg, g, grade_deg):
    return mass_kg * g * np.sin(np.radians(grade_deg))

def traction_force_required(v_m_per_s, a_m_per_s2, mass_kg, g, rho, cd, area_m2, grade_deg,
                            mu_rr_base=0.011, mu_rr_k=1.5e-5):
    f_rr = rolling_resistance_force(v_m_per_s, mass_kg, g, mu_rr_base, mu_rr_k)
    f_aero = aero_drag_force(v_m_per_s, rho, cd, area_m2)
    f_grad = gradient_force(mass_kg, g, grade_deg)
    f_accel = mass_kg * a_m_per_s2
    return f_rr + f_aero + f_grad + f_accel, f_rr, f_aero, f_grad, f_accel

def mechanical_power_W(force_N, v_m_per_s):
    return force_N * v_m_per_s  # W

def electrical_power_W(p_mech_W, motor_eff, drivetrain_eff, aux_W=0.0):
    if motor_eff <= 0 or drivetrain_eff <= 0:
        raise ValueError("Efficiencies must be positive")
    return p_mech_W / (motor_eff * drivetrain_eff) + aux_W
