# driving_cycles.py

import numpy as np
import csv

def load_csv_cycle(filepath):
    """
    Load a driving cycle CSV with columns: time_s, speed_kmh, grade_deg (optional)
    Returns arrays: t, v_m_per_s, grade_deg
    """
    t, v_kmh, grade = [], [], []
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            t.append(float(row['time_s']))
            v_kmh.append(float(row['speed_kmh']))
            if 'grade_deg' in row and row['grade_deg'] != '':
                grade.append(float(row['grade_deg']))
            else:
                grade.append(0.0)
    t = np.array(t)
    v_mps = np.array(v_kmh) / 3.6
    grade = np.array(grade)
    return t, v_mps, grade

def simple_wltp_like_cycle(total_time_s=1800, dt=1.0):
    """
    Simple placeholder cycle with urban + suburban + highway segments.
    Not official WLTP, but shaped similarly for demonstration.
    """
    t = np.arange(0, total_time_s + dt, dt)
    v = np.zeros_like(t, dtype=float)

    # segments in seconds
    urban = int(600/dt)
    suburban = int(600/dt)
    highway = int(600/dt)

    # Urban: average ~25 km/h with stops
    for i in range(urban):
        v[i] = max(0.0, (25/3.6) + 2/3.6 * np.sin(2*np.pi*i/60) - (i % 100 == 0)*5/3.6)

    # Suburban: ~50 km/h
    for i in range(urban, urban+suburban):
        v[i] = (50/3.6) + 3/3.6 * np.sin(2*np.pi*(i-urban)/90)

    # Highway: ~100 km/h
    for i in range(urban+suburban, urban+suburban+highway):
        v[i] = (100/3.6) + 5/3.6 * np.sin(2*np.pi*(i-urban-suburban)/120)

    grade = np.zeros_like(v)
    return t, v, grade
