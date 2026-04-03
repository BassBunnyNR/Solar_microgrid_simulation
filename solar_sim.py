import numpy as np

import matplotlib.pyplot as plt

# ---Constants---
# *** NOT REAL VALUES ***

SOLAR_CAPACITY_KW = 5.0 # Max Power of solar panels
SUNRISE_HOUR = 6 # Time the sun rises
SUNSET_HOUR = 18 # Time the sun sets
SYSTEM_EFFICIENCY = 0.85 # Representing 15% losses (dust, heat, inverter)
NOISE_LEVEL = 0.1 # Diviation of production

# ---Time Vector---
# Hour Resolution (0.1 hours - 240 Dots)

hours = np.arange(0,24,0.1)
solar_production = []

#Calculating the length of the day to normalize the sine wave
day_duration = SUNSET_HOUR - SUNRISE_HOUR

last_val = 0

for h in hours:
    if SUNRISE_HOUR <= h <= SUNSET_HOUR:
        # (h - SUNRISE_HOUR) / day_duration: Normalizes the current hour to a 0-1 scale 
        # multiplying by np.pi creates a half-cycle (0 to π) where sin is always positive
        angle = np.pi * (h - SUNRISE_HOUR) / day_duration

        # np.sin(angle): Calculates the sine value for the current angle
        raw_power = SOLAR_CAPACITY_KW * np.sin(angle)

        #  Calculation of diviation
        std_dev = raw_power * NOISE_LEVEL
        noisy_power = np.random.normal(raw_power, std_dev) #normal deviation

        # Applying efficiency factor on the noisy power
        actual_power = noisy_power * SYSTEM_EFFICIENCY

        # Using np.clip to ensure power is never negative
        # Argument 1: the value to check
        # Argument 2: minimum allowed, Argument 3: maximum allowed (The theoretical peak * efficiency)

        final_power = np.clip(actual_power, 0, SOLAR_CAPACITY_KW * SYSTEM_EFFICIENCY)
        smoothed_power = (0.7 * final_power) + (0.3 * last_val)
        solar_production.append(smoothed_power)
        last_val = smoothed_power

    else:
        solar_production.append(0) # No Production in Night

        
# --- Plotting the Graph ---

plt.figure(figsize=(12, 6))

# plt.plot: Creates the line graph
# alpha=0.8: Sets transparency
plt.plot(hours, solar_production, label='Solar Output (Adjusted)', color='gold', linewidth=2, alpha=0.8)

# plt.fill_between: Fills the area under the curve
plt.fill_between(hours, solar_production, color='orange', alpha=0.2)

# Setting axis labels and title
plt.xlabel('Hour of the Day [24h Format]')
plt.ylabel('Power Output [kW]')
plt.title('Solar Energy Production Simulation')

# plt.xticks: Customizes the intervals on the X-axis
plt.xticks(np.arange(0, 25, 1))

plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.legend()

# Display the final plot
plt.show()