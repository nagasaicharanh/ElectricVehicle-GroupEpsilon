# main.py

import numpy as np

from vehicle_parameters import BYD_SEAL_Premium_Params
from motor_model import MotorModel
from battery_model import BatteryModel
from driving_cycles import simple_wltp_like_cycle, load_csv_cycle
from simulation_engine import simulate_cycle, constant_speed_energy
from analysis_plots import plot_timeseries, plot_energy_vs_speed

def run_cycle_demo():
    # Load parameters
    p = BYD_SEAL_Premium_Params()

    # Instantiate models
    motor = MotorModel(p.motor_torque_max_Nm, p.motor_power_max_W, p.wheel_radius_m, p.motor_peak_eff)
    battery = BatteryModel(p.battery_capacity_Wh, p.v_nominal_V, p.v_min_V, p.v_max_V,
                           p.r_int_ohm, p.soc_min, p.soc_max, p.regen_eff)

    # Driving cycle
    t_s, v_mps, grade_deg = simple_wltp_like_cycle(total_time_s=1800, dt=1.0)
    # Alternatively load a CSV with columns: time_s, speed_kmh[, grade_deg]
    # t_s, v_mps, grade_deg = load_csv_cycle("wltp_subset.csv")

    # Simulate
    result = simulate_cycle(t_s, v_mps, grade_deg, p, motor, battery, dt_s=1.0, limit_top_speed=True)

    # Compute aggregates
    total_dist_km = result["distance_km"][-1]
    total_energy_kWh = result["total_energy_Wh"] / 1000.0
    avg_consumption_kWh_per_100km = (total_energy_kWh / total_dist_km) * 100.0 if total_dist_km > 0 else np.nan

    print("=== Cycle Summary ===")
    print(f"Distance: {total_dist_km:.2f} km")
    print(f"Energy Used: {total_energy_kWh:.2f} kWh")
    print(f"Average Consumption: {avg_consumption_kWh_per_100km:.2f} kWh/100km (Target WLTP: {p.wltp_energy_kWh_per_100km} kWh/100km)")
    print(f"Final SOC: {result['soc'][-1]:.3f}")

    # Plots
    plot_timeseries(result, title="BYD SEAL Premium - WLTP-like Cycle")

def constant_speed_sweep():
    p = BYD_SEAL_Premium_Params()
    motor = MotorModel(p.motor_torque_max_Nm, p.motor_power_max_W, p.wheel_radius_m, p.motor_peak_eff)

    speeds = np.arange(40, 141, 10)
    energies = []
    for s in speeds:
        pkW, e = constant_speed_energy(p, motor, speed_kmh=s, grade_deg=0.0)
        energies.append(e)
        print(f"{s:>3} km/h -> {pkW:5.1f} kW, {e:5.1f} kWh/100km")
    plot_energy_vs_speed(speeds, energies)

if __name__ == "__main__":
    # 1) Run WLTP-like cycle simulation
    run_cycle_demo()

    # 2) Run constant-speed energy sweep
    constant_speed_sweep()
