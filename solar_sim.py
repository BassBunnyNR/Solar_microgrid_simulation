import numpy as np
import matplotlib.pyplot as plt

# --- Functions Section ---

def generate_solar_production(hours, capacity_kw, sunrise_hour, sunset_hour, efficiency, noise_level):
    """
    Calculates solar production based on a sine wave with noise and smoothing.
    All logic is encapsulated here to keep the main code clean.
    """
    solar_production = []
    
    # Calculating the length of the day to normalize the sine wave
    day_duration = sunset_hour - sunrise_hour
    last_val = 0

    for h in hours:
        if sunrise_hour <= h <= sunset_hour:
            # (h - SUNRISE_HOUR) / day_duration: Normalizes the current hour to a 0-1 scale 
            # multiplying by np.pi creates a half-cycle (0 to π) where sin is always positive
            angle = np.pi * (h - sunrise_hour) / day_duration

            # np.sin(angle): Calculates the sine value for the current angle
            raw_power = capacity_kw * np.sin(angle)

            # Calculation of deviation
            std_dev = raw_power * noise_level
            noisy_power = np.random.normal(raw_power, std_dev) # normal deviation

            # Applying efficiency factor on the noisy power
            actual_power = noisy_power * efficiency

            # Using np.clip to ensure power is never negative
            # Argument 1: the value to check
            # Argument 2: minimum allowed, Argument 3: maximum allowed (The theoretical peak * efficiency)
            final_power = np.clip(actual_power, 0, capacity_kw * efficiency)
            
            # Smoothing the output (Correlation with previous value)
            smoothed_power = (0.7 * final_power) + (0.3 * last_val)
            solar_production.append(smoothed_power)
            last_val = smoothed_power

        else:
            solar_production.append(0) # No Production in Night
            last_val = 0 # Resetting last_val for the next day cycle
            
    return solar_production

def plot_solar_system(hours, solar_production, house_load):
    """
    Handles the visual representation of the data.
    """
    plt.figure(figsize=(12, 6))

    # plt.plot: Creates the line graph
    # alpha=0.8: Sets transparency
    plt.plot(hours, solar_production, label='Solar Output (Adjusted)', color='gold', linewidth=2, alpha=0.8)
    plt.plot(hours, house_load, label='House Load', color='blue')
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

def generate_load_data(hours, base_load, morning_peak_kw, evening_peak_kw):
    """
    Generates a typical residential 'Duck Curve' load profile.
    Uses Gaussian peaks for morning and evening activities.
    """
    load_profile = []
    
    for h in hours:
        # 1. Base load (always on)
        current_load = base_load
        
        # 2. Morning peak (Centered at 08:00, width of 1.5 hours)
        morning_peak = morning_peak_kw * np.exp(-((h - 8)**2) / (2 * 1.5**2))
        
        # 3. Evening peak (Centered at 20:00, width of 2.5 hours)
        evening_peak = evening_peak_kw * np.exp(-((h - 20)**2) / (2 * 2.5**2))
        
        # Total load for this hour + some small random noise
        total = current_load + morning_peak + evening_peak + np.random.normal(0, 0.05)
        
        load_profile.append(np.clip(total, 0, None)) # Ensure no negative load
        
    return load_profile

# --- Main Execution Section ---

def main():
    # ---Constants---
    # *** NOT REAL VALUES ***
    SOLAR_CAPACITY_KW = 5.0 # Max Power of solar panels
    SUNRISE_HOUR = 6        # Time the sun rises
    SUNSET_HOUR = 18       # Time the sun sets
    SYSTEM_EFFICIENCY = 0.85 # Representing 15% losses (dust, heat, inverter)
    NOISE_LEVEL = 0.1      # Deviation of production

    # ---Time Vector---
    # Hour Resolution (0.1 hours - 240 Dots)
    hours = np.arange(0, 24, 0.1)

    # Generate the data using our function
    solar_data = generate_solar_production(
        hours, 
        SOLAR_CAPACITY_KW, 
        SUNRISE_HOUR, 
        SUNSET_HOUR, 
        SYSTEM_EFFICIENCY, 
        NOISE_LEVEL
    )

    load_data = generate_load_data(
        hours,
        base_load=0.5,
        morning_peak_kw=1.5,
        evening_peak_kw=3.5
    )
    # Plot the results
    plot_solar_system(hours, solar_data, load_data)

# This standard boilerplate ensures the script runs only if executed directly
if __name__ == "__main__":
    main()