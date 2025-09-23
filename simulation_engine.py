# simulation_engine.py

import numpy as np
from physics import traction_force_required, mechanical_power_W, electrical_power_W

def simulate_cycle(t_s, v_mps, grade_deg,
                   params, motor_model, battery_model,
                   dt_s=1.0,
                   limit_top_speed=True):
    """
    Forward simulation over a velocity-time profile.
    Returns dict with time series and aggregates.
    """
    n = len(t_s)
    a_mps2 = np.zeros(n)
    f_total = np.zeros(n)
    f_rr = np.zeros(n)
    f_aero = np.zeros(n)
    f_grad = np.zeros(n)
    f_accel = np.zeros(n)
    p_mech = np.zeros(n)
    p_elec = np.zeros(n)
    p_batt = np.zeros(n)
    soc = np.zeros(n)
    dist_m = np.zeros(n)

    # numerical acceleration
    a_mps2[1:] = np.diff(v_mps)/dt_s

    # clamp to top speed if desired
    if limit_top_speed:
        v_mps = np.minimum(v_mps, params.max_speed_kmh_official/3.6)

    total_energy_Wh = 0.0
    soc[0] = battery_model.soc

    for i in range(n):
        v = v_mps[i]
        a = a_mps2[i]
        grade = grade_deg[i] if i < len(grade_deg) else 0.0

        f_req, frr, fa, fg, facc = traction_force_required(
            v, a, params.mass_kg, params.g_m_per_s2, params.air_density_kg_per_m3,
            params.cd, params.frontal_area_m2, grade,
            params.mu_rr_base, params.mu_rr_k
        )
        f_total[i], f_rr[i], f_aero[i], f_grad[i], f_accel[i] = f_req, frr, fa, fg, facc

        # Motor wheel torque limit
        wheel_torque_avail = motor_model.wheel_torque_from_motor(v, params.drivetrain_eff)
        f_motor_max = wheel_torque_avail / max(params.wheel_radius_m, 1e-6)

        # Limit traction by available motor force (no slip model, simplified)
        f_deliver = np.minimum(f_req, f_motor_max)

        # Mechanical power (>=0 for traction; braking handled as negative electrical)
        p_mech_i = mechanical_power_W(f_deliver, v)
        p_mech[i] = p_mech_i

        # Convert to electrical power draw (+aux)
        # If decelerating (p_mech < 0), treat as potential regen
        if p_mech_i >= 0:
            p_elec_i = electrical_power_W(p_mech_i, params.motor_peak_eff, params.drivetrain_eff, params.aux_power_W)
            p_batt_i = p_elec_i
        else:
            # Regen (negative mech power). Recover with regen efficiency, minus aux.
            p_regen = -p_mech_i * params.motor_peak_eff * params.drivetrain_eff * params.regen_eff
            p_batt_i = params.aux_power_W - p_regen  # net battery power
        p_elec[i] = max(p_mech_i, 0.0)  # store mech traction power for reference
        p_batt[i] = p_batt_i

        # Battery step (returns Wh drawn, positive)
        e_Wh = battery_model.step(p_batt_i, dt_s)
        total_energy_Wh += e_Wh

        soc[i] = battery_model.soc
        dist_m[i] = v * dt_s

    result = {
        "t_s": t_s,
        "v_mps": v_mps,
        "a_mps2": a_mps2,
        "f_total_N": f_total,
        "f_rr_N": f_rr,
        "f_aero_N": f_aero,
        "f_grad_N": f_grad,
        "f_accel_N": f_accel,
        "p_mech_W": p_mech,
        "p_batt_W": p_batt,
        "soc": soc,
        "distance_km": np.cumsum(dist_m)/1000.0,
        "total_energy_Wh": total_energy_Wh,
    }
    return result

def constant_speed_energy(params, motor_model, speed_kmh=100.0, grade_deg=0.0):
    """
    Computes consumption at steady speed (no accel).
    Returns power (kW) and energy (kWh/100km).
    """
    v = speed_kmh / 3.6
    f_req, *_ = traction_force_required(
        v, 0.0, params.mass_kg, params.g_m_per_s2, params.air_density_kg_per_m3,
        params.cd, params.frontal_area_m2, grade_deg,
        params.mu_rr_base, params.mu_rr_k
    )
    p_mech = f_req * v
    # Use peak efficiencies as a first approximation
    p_elec = p_mech / (params.motor_peak_eff * params.drivetrain_eff) + params.aux_power_W
    energy_kWh_per_100km = (p_elec/1000.0) * (100.0 / speed_kmh)
    return p_elec/1000.0, energy_kWh_per_100km
