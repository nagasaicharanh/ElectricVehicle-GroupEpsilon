# Electric Vehicle Simulation Framework

A comprehensive Python-based simulation framework for electric vehicle performance analysis, specifically modeling the BYD SEAL Premium. This tool provides accurate energy consumption predictions and efficiency analysis across various driving scenarios.

## Key Features

- **WLTP Cycle Simulation**: Simulates standardized driving cycles to predict real-world energy consumption and range
- **Motor & Battery Modeling**: Physics-based models for electric motor efficiency and battery behavior including SOC management
- **Constant Speed Analysis**: Energy consumption analysis across different constant speeds (40-140 km/h)
- **Performance Metrics**: Calculates key metrics including kWh/100km consumption, total range, and efficiency comparisons
- **Visualization Tools**: Generates time-series plots and energy consumption charts for analysis
- **Flexible Input**: Supports both built-in WLTP-like cycles and custom CSV driving cycle data

## Quick Start

Run the main simulation to analyze BYD SEAL Premium performance across WLTP-like driving conditions and generate comprehensive energy consumption reports with visualization.


The simulation outputs include distance traveled, total energy consumption, average consumption rates compared to WLTP targets, and final battery state of charge with accompanying performance plots.

## Output Example
=== Cycle Summary ===
Distance: 23.25 km
Energy Used: 4.18 kWh
Average Consumption: 17.98 kWh/100km (Target WLTP: 18.5 kWh/100km)
Final SOC: 0.950

Google Colab Link: https://colab.research.google.com/drive/1-bezErEGDKHMqPjqfWFYA9N3MXZ-r6UU?usp=sharing

The scripts can be run online on the cloud instance of Google colab by just clicking the above link and running the cell.


