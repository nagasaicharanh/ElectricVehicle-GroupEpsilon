import matplotlib.pyplot as plt

def plot_timeseries(result, title="Simulation"):
    t = result["t_s"]
    v_kmh = result["v_mps"] * 3.6
    p_batt_kW = result["p_batt_W"] / 1000.0
    f_total = result["f_total_N"]
    f_aero = result["f_aero_N"]
    f_rr = result["f_rr_N"]
    soc = result["soc"]

    fig, axs = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

    # 1) Speed
    axs[0].plot(t, v_kmh, label="Speed (km/h)")
    axs[0].set_ylabel("km/h")
    axs[0].grid(True)
    axs[0].legend()

    # 2) Battery Power
    axs[1].plot(t, p_batt_kW, label="Battery Power (kW)")
    axs[1].set_ylabel("kW")
    axs[1].grid(True)
    axs[1].legend()

    # 3) Forces
    axs[2].plot(t, f_total, label="Total Force (N)")
    axs[2].plot(t, f_aero, label="Aero (N)", alpha=0.7)
    axs[2].plot(t, f_rr, label="Rolling (N)", alpha=0.7)
    axs[2].set_ylabel("N")
    axs[2].grid(True)
    axs[2].legend()

    # 4) SOC
    axs[3].plot(t, soc, label="SOC")
    axs[3].set_ylabel("SOC [-]")
    axs[3].set_xlabel("Time (s)")
    axs[3].grid(True)
    axs[3].legend()

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()


def plot_energy_vs_speed(speeds_kmh, energy_kWh_per_100km):
    plt.figure(figsize=(8, 5))
    plt.plot(speeds_kmh, energy_kWh_per_100km, marker="o")
    plt.grid(True)
    plt.xlabel("Speed (km/h)")
    plt.ylabel("Energy (kWh/100km)")
    plt.title("Constant-Speed Energy Consumption")
    plt.show()
