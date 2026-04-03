import numpy as np
import matplotlib.pyplot as plt

# --- Functions Section ---

# Input Data
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

# Load Data
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

# Defining relay working conditions
# When we have surplass of 0.2KW, turns on
def simulate_relay_logic(net_power, threshold=0.2):
    """
    Decides when to switch the relay ON (1) or OFF (0)
    """
    relay_status = []
    for val in net_power:
        if val > threshold:
            relay_status.append(1) # Relay ON
        else:
            relay_status.append(0) # Relay OFF
    return np.array(relay_status) # Convert to numpy array

# Graph plotting
def plot_solar_system(hours, solar_production, house_load, relay_status):
    """
    Visualizes Energy Profiles and Relay Status with Dark Mode.
    Includes surplus fill and fixed status bar.
    """
    # Enable Dark Mode
    plt.style.use('dark_background')
    
    # Ensure everything is a numpy array for correct indexing and operations
    h = np.asarray(hours)
    s = np.asarray(solar_production)
    l = np.asarray(house_load)
    r = np.asarray(relay_status)
    net_p = s - l

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                   gridspec_kw={'height_ratios': [5, 1]}, 
                                   sharex=True)
    plt.subplots_adjust(hspace=0.1)

    # --- Top Plot: Energy ---
    ax1.plot(h, s, label='Solar Output', color="#D5BC2B", linewidth=2)
    ax1.plot(h, l, label='House Load', color='#00FFFF', linewidth=1.5)
    ax1.plot(h, net_p, label='Net Power (Surplus)', color='#32CD32', linestyle='--', alpha=0.6)
    
    # Add Fill between Net Power and 0 (The Surplus Zone)
    ax1.fill_between(h, net_p, 0, where=(net_p > 0), color='#32CD32', alpha=0.15, label='Surplus Energy')
    ax1.fill_between(h, net_p, 0, where=(net_p <= 0), color='red', alpha=0.05)

    ax1.set_ylabel('Power [kW]')
    ax1.set_title('Solar Microgrid Simulation - Energy & Relay Status')
    ax1.grid(True, linestyle=':', alpha=0.3)
    ax1.legend(loc='upper right')
    ax1.set_xticks(np.arange(0, 25, 1))

    # --- Bottom Plot: Relay Status Bar ---
    # Fix: Draw the bar by checking each segment
    # We use 'where' logic with the full range of h
    ax2.fill_between(h, 0, 1, where=(r == 1), color='lime', alpha=0.7, step='post')
    ax2.fill_between(h, 0, 1, where=(r == 0), color='red', alpha=0.7, step='post')

    ax2.set_yticks([]) 
    ax2.set_ylim(0, 1) 
    ax2.set_xlabel('Hour of the Day [24h Format]')
    ax2.set_ylabel('Relay', rotation=0, labelpad=20, verticalalignment='center')
    
    plt.show()


# --- Main Execution Section ---

def main():
    # ---Constants---
    # *** NOT REAL VALUES ***
    SOLAR_CAPACITY_KW = 5.0 # Max Power of solar panels
    SUNRISE_HOUR = 6 # Time the sun rises
    SUNSET_HOUR = 18 # Time the sun sets
    SYSTEM_EFFICIENCY = 0.85 # Representing 15% losses (dust, heat, inverter)
    NOISE_LEVEL = 0.1 # Deviation of production

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
   
    # Calculate Net Power (Surplus = Positive, Deficit = Negative)
    # Using np.array for element-wise subtraction
    net_power = np.array(solar_data) - np.array(load_data)

    # Generate 0/1 as Relay Status
    relay_status_results = simulate_relay_logic(net_power, threshold=0.2)

    # Plot the results
    plot_solar_system(hours, solar_data, load_data, relay_status_results)

# This standard boilerplate ensures the script runs only if executed directly
if __name__ == "__main__":
    main()