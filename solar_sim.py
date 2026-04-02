import numpy as np
import matplotlib.pyplot as plt

# ---Constants---
# *** NOT REAL VALUES ***

SOLAR_CAPACITY_KW = 5.0 # Max Power of solar panels
SUNRISE_HOUR = 6 # Time the sun rises
SUNSET_HOUR = 18 # Time the sun sets

# ---Creating Time-Line---
# Hour Resolution (24 Dots)

hours = np.arange(0,24,1)
solar_production = []

for h in hours:
    if SUNRISE_HOUR <= h <= SUNSET_HOUR:
        #Power calculation based on half sin period
        day_length = SUNSET_HOUR - SUNRISE_HOUR
        power = SOLAR_CAPACITY_KW * np.sin(np.pi * (h - SUNRISE_HOUR / day_length))
        solar_production.append(power)
    else:
        solar_production.append(0) # No Production in Night

        
# --- Plotting the Graph ---

plt.figure(figsize=(10, 5))
plt.plot(hours, solar_production, label='Solar Production', color='pink', marker='o')
plt.xticks(hours) #Presenting all hours on the axis
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.title("Solar Generation Profile - Initial Model")
plt.show()
