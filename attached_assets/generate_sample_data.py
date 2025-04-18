import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define counties
counties = [
    'Dublin', 'Galway', 'Carlow', 'Clare', 'Cork', 'Cavan', 'Westmeath', 
    'Mayo', 'Sligo', 'Meath', 'Tipperary', 'Donegal', 'Wexford', 'Roscommon'
]

# Create synthetic weather data for Irish counties from 2015-2022
start_date = datetime(2015, 1, 1)
end_date = datetime(2022, 12, 31)
delta = timedelta(hours=6)  # 4 measurements per day

# Base temperature and rainfall patterns for Ireland
base_temp = {
    'winter': 5,      # Average winter temperature
    'spring': 10,     # Average spring temperature
    'summer': 15,     # Average summer temperature
    'autumn': 10      # Average autumn temperature
}

base_rain = {
    'winter': 3.5,    # Average winter rainfall per day
    'spring': 2.0,    # Average spring rainfall per day
    'summer': 1.5,    # Average summer rainfall per day
    'autumn': 3.0     # Average autumn rainfall per day
}

# County-specific modifiers (some counties are warmer/colder, wetter/drier)
county_modifiers = {
    'Dublin': {'temp': 0.5, 'rain': -0.3},     # Slightly warmer, less rain
    'Galway': {'temp': -0.2, 'rain': 1.0},     # Cooler, more rain
    'Carlow': {'temp': 0.3, 'rain': -0.1},     # Warmer, slightly less rain
    'Clare': {'temp': -0.1, 'rain': 0.8},      # Slightly cooler, more rain
    'Cork': {'temp': 1.0, 'rain': 0.6},        # Warmer, more rain
    'Cavan': {'temp': -0.5, 'rain': 0.2},      # Cooler, slightly more rain
    'Westmeath': {'temp': 0.0, 'rain': 0.0},   # Average 
    'Mayo': {'temp': -1.0, 'rain': 1.2},       # Colder, much more rain
    'Sligo': {'temp': -0.8, 'rain': 0.8},      # Colder, more rain
    'Meath': {'temp': 0.2, 'rain': -0.1},      # Slightly warmer, less rain
    'Tipperary': {'temp': 0.7, 'rain': -0.3},  # Warmer, less rain
    'Donegal': {'temp': -0.7, 'rain': 0.5},    # Colder, more rain
    'Wexford': {'temp': 0.4, 'rain': 0.0},     # Warmer, average rain
    'Roscommon': {'temp': -0.3, 'rain': 0.3}   # Cooler, more rain
}

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'autumn'

# Generate data
data = []
current_date = start_date
while current_date <= end_date:
    season = get_season(current_date)
    
    for county in counties:
        # Get base values for the season
        base_temp_value = base_temp[season]
        base_rain_value = base_rain[season] / 4  # Divide by 4 as we have 4 measurements per day
        
        # Apply county-specific modifiers
        modifier = county_modifiers[county]
        temp_modifier = modifier['temp']
        rain_modifier = modifier['rain']
        
        # Add random variations
        temp_variation = np.random.normal(0, 1.5)  # Random temperature variation
        rain_variation = abs(np.random.normal(0, 0.5))  # Random rain variation (always positive)
        
        # Calculate final values
        temperature = base_temp_value + temp_modifier + temp_variation
        rainfall = max(0, (base_rain_value + rain_modifier + rain_variation) / 4)  # Ensure non-negative
        
        # Seasonal adjustments
        if season == 'winter':
            # More variability in winter
            temperature += np.random.normal(0, 2.0)
            rainfall *= np.random.uniform(0.8, 1.5)
        elif season == 'summer':
            # Occasional summer showers
            if np.random.random() < 0.25:
                rainfall *= np.random.uniform(1.5, 3.0)
            else:
                rainfall *= np.random.uniform(0.1, 0.9)
        
        # Add entry to dataset
        data.append({
            'date': current_date.strftime('%d-%m-%Y %H:%M'),
            'county': county,
            'temp': round(temperature, 2),
            'rain': round(rainfall, 2)
        })
    
    current_date += delta

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('counties_with_data_2015_2022.csv', index=False)
print(f"Generated sample weather data for {len(counties)} Irish counties from 2015-2022")
print(f"Total records: {len(df)}")
print(f"Sample data:")
print(df.head())