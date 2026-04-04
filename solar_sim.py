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

# System modes - Selling/Buying/Charging/Discharging
def simulate_smart_grid(hours, net_power, battery_capacity=10.0):
    """
    Simulates a smart home with battery priority.
    battery_capacity: kWh (Standard home battery)
    """
    BUY_PRICE = 0.60 
    SELL_PRICE = 0.45
    
    soc = 0 # State of Charge in kWh
    daily_balance = 0
    battery_history = []
    
    # Modes: 0=Buying, 1=Charging, 2=Selling, 3=Discharging
    grid_mode = [] 

    dt = 0.1 # Hour step

    for p in net_power:
        if p > 0: # --- SURPLUS ---
            if soc < battery_capacity:
                # Priority 1: Charge Battery
                charge = p * dt
                soc = min(battery_capacity, soc + charge)
                grid_mode.append(1) # Charging
            else:
                # Priority 2: Sell to Grid
                sell_revenue = p * dt * SELL_PRICE
                daily_balance += sell_revenue
                grid_mode.append(2) # Selling
        
        else: # --- DEFICIT ---
            needed = abs(p) * dt
            if soc > 0:
                # Priority 1: Use Battery
                use_from_batt = min(soc, needed)
                soc -= use_from_batt
                needed -= use_from_batt
                grid_mode.append(3) # Discharging
            
            if needed > 0:
                # Priority 2: Buy from Grid
                cost = needed * BUY_PRICE
                daily_balance -= cost
                if p < 0 and soc <= 0: grid_mode.append(0) # Buying

        battery_history.append((soc / battery_capacity) * 100)

    return battery_history, daily_balance, grid_mode

# Financial calculations
def show_financial_report(daily_balance, load_data):
    # Total consumption in kWh (Power * Time)
    total_consumed_kwh = np.sum(load_data) * 0.1
    # Cost if we had NO solar system
    original_cost = total_consumed_kwh * 0.60
    # Current bill is the absolute value of our daily_balance (if negative)
    current_bill = abs(daily_balance) if daily_balance < 0 else 0
    # Total savings
    daily_savings = original_cost - current_bill

    # --- Print Report to Terminal ---
    print("\n" + "="*35)
    print("      DAILY ENERGY REPORT")
    print("="*35)
    print(f"Original Cost (No Solar): ₪{original_cost:.2f}")
    print(f"Current Grid Bill:        ₪{current_bill:.2f}")
    print(f"-----------------------------------")
    print(f"NET SAVINGS TODAY:        ₪{daily_savings:.2f}")
    print("="*35 + "\n")


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
    ax1.fill_between(h, net_p, 0, where=(net_p > 0), color='#32CD32', alpha=0.25, label='Surplus Energy')
    ax1.fill_between(h, net_p, 0, where=(net_p <= 0), color='red', alpha=0.25)

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

    # Generating and plotting battery and grid parameters
def plot_battery_status(hours, battery_history, grid_mode):
    """Visualizes battery SOC and grid operational modes."""
    plt.style.use('dark_background')
    
    # Force alignment of data lengths
    min_size = min(len(hours), len(battery_history), len(grid_mode))
    h = np.asarray(hours)[:min_size]
    batt = np.asarray(battery_history)[:min_size]
    mode = np.asarray(grid_mode)[:min_size]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [4, 1]}, sharex=True)
    plt.subplots_adjust(hspace=0.1)
    
    # Top Plot: Battery Charge Level
    ax1.plot(h, batt, color='#00FF00', linewidth=2, label='Battery SOC %')
    ax1.fill_between(h, batt, color='#00FF00', alpha=0.2)
    ax1.set_ylabel('Charge [%]')
    ax1.set_ylim(0, 105)
    ax1.set_title('Storage Logic: Battery SOC & Grid Interaction')
    ax1.grid(True, linestyle=':', alpha=0.3)

    # Bottom Plot: Grid Modes
    # 0:Buy (Red), 1:Charge (Lime), 2:Sell (Cyan), 3:Discharge (Orange)
    colors = {0: 'red', 1: 'lime', 2: 'cyan', 3: 'orange'}
    for m in range(4):
        ax2.fill_between(h, 0, 1, where=(mode == m), color=colors[m], alpha=0.8, step='post')
    
    ax2.set_yticks([])
    ax2.set_ylabel('Mode')
    ax2.set_xlabel('Hour of the Day [24h Format]')
    
    # Add a small legend for the modes
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color=colors[i], lw=4) for i in range(4)]
    ax2.legend(custom_lines, ['Buy', 'Charge', 'Sell', 'Discharge'], 
               loc='upper center', bbox_to_anchor=(0.5, -0.5), ncol=4, fontsize='small')
    
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

    # Getting Battery and Grid information
    battery_history, daily_balance, grid_mode = simulate_smart_grid(hours, net_power, battery_capacity=10.0)

    # ---MENU---
    while True:
        print("---Control Menu---")
        print("1. Production Graphs\n2. Battery Status\n3. Financial Report\n4. Exit")
        choice = input("Select: ")

        if choice == '1':
            plot_solar_system(hours, solar_data, load_data, relay_status_results)
        elif choice == '2':
            plot_battery_status(hours, battery_history, grid_mode)
        elif choice == '3':
            show_financial_report(daily_balance, load_data)
        elif choice == '4':
            break

    # Plot the results

# This standard boilerplate ensures the script runs only if executed directly
if __name__ == "__main__":
    main()