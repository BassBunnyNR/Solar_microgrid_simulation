# Smart Solar Microgrid Simulator ☀️

A Python-based simulation of a residential solar energy system, developed to bridge the gap between theoretical electrical engineering and practical hardware implementation during times of uncertainty, as a side project during the war.

## Overview
This project simulates a 24-hour cycle of a home energy system. It models solar production, household consumption, and smart battery management.

## Key Features
* **Energy Telemetry:** High-resolution (6-min intervals) simulation of solar output including efficiency losses and environmental noise.
* **Smart Storage Logic:** Automated relay control for battery charging and discharging priorities.
* **Grid Interaction:** Real-time monitoring of energy buy/sell states based on battery SOC (State of Charge).
* **Financial Reporting:** ROI analysis comparing theoretical grid costs vs. actual solar savings.

## How to Run
1. Ensure you have `numpy` and `matplotlib` installed:
   ```bash
   pip install numpy matplotlib

2. Run the script:
python solar_sim.py

3. Use the interactive menu to toggle between Production Graphs, Battery Status, and Financial Reports.

Future Plans
The logic developed here is designed to be ported to an ESP32 microcontroller using current sensors and physical relays to manage a real small-scale solar setup.