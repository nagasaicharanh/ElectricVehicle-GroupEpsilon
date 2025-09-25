# range_simulation.py

import numpy as np
from physics import traction_force_required, mechanical_power_W
from motor_model import MotorModel
from battery_model import BatteryModel

def simulate_full_range_over_cycle(params,
                                   motor_model: MotorModel,
                                   battery_model: BatteryModel,
                                   t_cycle_s: np.ndarray,
                                   v_cycle_mps: np.ndarray,
                                   grade_cycle_deg: np.ndarray,
                                   limit_top_speed: bool = True,
                                   max_hours: float = 12.0):
    """
    Loop the given driving cycle until the battery reaches soc_min.
    Returns summary metrics and a small preview of the first cycle’s traces.
    """
    # Basic checks
    if len(t_cycle_s) < 2:
        raise ValueError("Cycle must have at least two time samples")
    dt = float(t_cycle_s[1] - t_cycle_s[0])
    if dt <= 0:
        raise ValueError("Cycle time step must be positive and uniform")

    n = len(t_cycle_s)
    v_cycle = v_cycle_mps.copy()
    if limit_top_speed:
        v_cap = params.max_speed_kmh_official / 3.6
        v_cycle = np.minimum(v_cycle, v_cap)

    # Precompute reference accelerations for the cycle (forward difference)
    a_cycle = np.zeros_like(v_cycle)
    a_cycle[:-1] = np.diff(v_cycle) / dt
    a_cycle[-1] = (v_cycle[0] - v_cycle[-1]) / dt  # wrap acceleration at boundary

    total_dist_m = 0.0
    total_time_s = 0.0
    total_energy_Wh = 0.0

    # Optional small preview buffers (only first pass, to avoid huge memory)
    preview_len = min(n, 2000)
    preview = {
        "t_s": t_cycle_s[:preview_len].copy(),
        "v_mps": v_cycle[:preview_len].copy(),
        "soc": np.zeros(preview_len),
        "p_batt_W": np.zeros(preview_len),
        "f_total_N": np.zeros(preview_len),
        "f_rr_N": np.zeros(preview_len),
        "f_aero_N": np.zeros(preview_len),
    }
    captured_preview = False

    max_steps = int(max_hours * 3600.0 / dt)
    steps = 0

    while battery_model.soc > params.soc_min + 1e-12 and steps < max_steps:
        for i in range(n):
            if battery_model.soc <= params.soc_min + 1e-12:
                break

            v = v_cycle[i]
            a = a_cycle[i]
            grade = grade_cycle_deg[i] if i < len(grade_cycle_deg) else 0.0

            # Longitudinal forces (demand)
            f_req, f_rr, f_aero, f_grad, f_acc = traction_force_required(
                v, a,
                params.mass_kg, params.g_m_per_s2,
                params.air_density_kg_per_m3,
                params.cd, params.frontal_area_m2,
                grade,
                params.mu_rr_base, params.mu_rr_k
            )

            # Motor-limited traction
            wheel_torque_avail = motor_model.wheel_torque_from_motor(v, params.drivetrain_eff)
            f_motor_max = wheel_torque_avail / max(params.wheel_radius_m, 1e-6)
            f_deliver = np.minimum(f_req, f_motor_max)

            # Mechanical power at wheels
            p_mech = mechanical_power_W(f_deliver, v)

            # Electrical/battery power with aux and regen handling (consistent with simulate_cycle)
            if p_mech >= 0:
                p_batt = p_mech / (params.motor_peak_eff * params.drivetrain_eff) + params.aux_power_W
            else:
                p_regen = (-p_mech) * params.motor_peak_eff * params.drivetrain_eff * params.regen_eff
                p_batt = params.aux_power_W - p_regen

            # Advance battery
            e_Wh = battery_model.step(p_batt, dt)
            total_energy_Wh += e_Wh

            # Distance and time
            total_dist_m += v * dt
            total_time_s += dt
            steps += 1

            # Capture a short preview (first pass only)
            if not captured_preview and i < preview_len:
                preview["soc"][i] = battery_model.soc
                preview["p_batt_W"][i] = p_batt
                preview["f_total_N"][i] = f_req
                preview["f_rr_N"][i] = f_rr
                preview["f_aero_N"][i] = f_aero

        if not captured_preview:
            captured_preview = True

    total_dist_km = total_dist_m / 1000.0
    total_time_h = total_time_s / 3600.0
    total_energy_kWh = total_energy_Wh / 1000.0
    avg_consumption_kWh_per_100km = np.nan
    if total_dist_km > 1e-6:
        avg_consumption_kWh_per_100km = (total_energy_kWh / total_dist_km) * 100.0

    return {
        "range_km": total_dist_km,
        "drive_time_h": total_time_h,
        "energy_used_kWh": total_energy_kWh,
        "avg_consumption_kWh_per_100km": avg_consumption_kWh_per_100km,
        "final_soc": battery_model.soc,
        "preview": preview,
        "dt_s": dt,
        "steps": steps
    }


def constant_speed_range_estimate(params,
                                  motor_model: MotorModel,
                                  battery_model: BatteryModel,
                                  speed_kmh: float,
                                  grade_deg: float = 0.0):
    """
    Closed-form estimate based on steady-state consumption:
    usable_Wh / (Wh per km at the specified speed).
    """
    v = speed_kmh / 3.6
    # Forces
    f_req, *_ = traction_force_required(
        v, 0.0,
        params.mass_kg, params.g_m_per_s2,
        params.air_density_kg_per_m3,
        params.cd, params.frontal_area_m2,
        grade_deg,
        params.mu_rr_base, params.mu_rr_k
    )
    p_mech = f_req * v
    p_elec = p_mech / (params.motor_peak_eff * params.drivetrain_eff) + params.aux_power_W  # W
    wh_per_km = (p_elec / 1000.0) * (1000.0 / speed_kmh)  # (kW * s) normalized to Wh/km via speed
    # Actually, p_elec is W; energy per km at steady speed: Wh/km = (p_elec W) / (v m/s) * (1/3600) * 1000
    # Simpler: kWh/100km = (p_elec/1000) * (100/speed_kmh); so Wh/km = 10 * (p_elec/1000) / speed_kmh * 1000 = (p_elec * 0.01) / speed_kmh
    wh_per_km = (p_elec * 0.01) / max(speed_kmh, 1e-6)
    range_km = ((battery_model.soc - params.soc_min) * params.battery_capacity_Wh) / max(wh_per_km, 1e-9)
    return {
        "speed_kmh": speed_kmh,
        "consumption_Wh_per_km": wh_per_km,
        "range_km": range_km
    }
