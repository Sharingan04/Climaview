from datetime import datetime
import pandas as pd
import numpy as np

def format_weather_data(api_data):
    """Format raw weather API data into a structured dictionary.
    
    Args:
        api_data (dict): Raw data from OpenWeatherMap API
        
    Returns:
        dict: Formatted weather data
    """
    # Extract main weather data
    weather_main = api_data['weather'][0]['main'] if 'weather' in api_data and len(api_data['weather']) > 0 else "Unknown"
    weather_description = api_data['weather'][0]['description'] if 'weather' in api_data and len(api_data['weather']) > 0 else "Unknown"
    
    # Extract coordinates
    lat = api_data['coord']['lat'] if 'coord' in api_data and 'lat' in api_data['coord'] else None
    lon = api_data['coord']['lon'] if 'coord' in api_data and 'lon' in api_data['coord'] else None
    
    # Create formatted data dictionary
    formatted_data = {
        'city': api_data['name'],
        'country': api_data['sys']['country'] if 'sys' in api_data and 'country' in api_data['sys'] else "Unknown",
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'temperature': api_data['main']['temp'] if 'main' in api_data and 'temp' in api_data['main'] else None,
        'feels_like': api_data['main']['feels_like'] if 'main' in api_data and 'feels_like' in api_data['main'] else None,
        'temp_min': api_data['main']['temp_min'] if 'main' in api_data and 'temp_min' in api_data['main'] else None,
        'temp_max': api_data['main']['temp_max'] if 'main' in api_data and 'temp_max' in api_data['main'] else None,
        'pressure': api_data['main']['pressure'] if 'main' in api_data and 'pressure' in api_data['main'] else None,
        'humidity': api_data['main']['humidity'] if 'main' in api_data and 'humidity' in api_data['main'] else None,
        'wind_speed': api_data['wind']['speed'] if 'wind' in api_data and 'speed' in api_data['wind'] else None,
        'wind_deg': api_data['wind']['deg'] if 'wind' in api_data and 'deg' in api_data['wind'] else None,
        'clouds': api_data['clouds']['all'] if 'clouds' in api_data and 'all' in api_data['clouds'] else None,
        'weather_main': weather_main,
        'weather_description': weather_description,
        'latitude': lat,
        'longitude': lon
    }
    
    return formatted_data

def format_date(date_str):
    """Format a date string for display.
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD HH:MM:SS'
        
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_str

def get_weather_icon(weather_main):
    """Get a weather icon based on the main weather condition.
    
    Args:
        weather_main (str): Main weather condition from API
        
    Returns:
        str: Weather emoji icon
    """
    weather_icons = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Smoke': '🌫️',
        'Haze': '🌫️',
        'Dust': '🌫️',
        'Fog': '🌫️',
        'Sand': '🌫️',
        'Ash': '🌫️',
        'Squall': '💨',
        'Tornado': '🌪️'
    }
    
    return weather_icons.get(weather_main, '🌡️')

def load_ireland_weather_data():
    """Load Ireland county weather data from CSV file.
    If file doesn't exist, generate sample data.
    
    Returns:
        pandas.DataFrame: Data containing weather information
    """
    try:
        # Try to load the data
        df = pd.read_csv('counties_with_data_2015_2022.csv')
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y %H:%M')
        
        # Create year and month columns for easier filtering
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        return df
    except Exception as e:
        # If file doesn't exist, generate sample data
        print(f"Error loading Ireland weather data: {e}")
        print("Generating sample weather data...")
        return generate_sample_ireland_data()

def generate_sample_ireland_data():
    """Generate sample weather data for Irish counties.
    
    Returns:
        pandas.DataFrame: Sample weather data
    """
    # List of Irish counties
    counties = [
        'Dublin', 'Galway', 'Carlow', 'Clare', 'Cork', 'Cavan', 'Westmeath',
        'Mayo', 'Sligo', 'Meath', 'Tipperary', 'Donegal', 'Wexford', 'Roscommon'
    ]
    
    # County-specific base temperatures and rainfall patterns
    county_baselines = {
        'Dublin': {'temp': 9.5, 'rain': 2.5, 'temp_var': 5.0, 'rain_var': 1.0},
        'Galway': {'temp': 9.0, 'rain': 3.0, 'temp_var': 4.5, 'rain_var': 1.5},
        'Carlow': {'temp': 9.8, 'rain': 2.3, 'temp_var': 5.2, 'rain_var': 1.0},
        'Clare': {'temp': 9.2, 'rain': 2.8, 'temp_var': 4.7, 'rain_var': 1.3},
        'Cork': {'temp': 10.0, 'rain': 3.2, 'temp_var': 5.0, 'rain_var': 1.6},
        'Cavan': {'temp': 8.7, 'rain': 2.6, 'temp_var': 5.0, 'rain_var': 1.2},
        'Westmeath': {'temp': 9.0, 'rain': 2.4, 'temp_var': 5.0, 'rain_var': 1.1},
        'Mayo': {'temp': 8.5, 'rain': 3.5, 'temp_var': 4.5, 'rain_var': 1.8},
        'Sligo': {'temp': 8.3, 'rain': 3.3, 'temp_var': 4.3, 'rain_var': 1.7},
        'Meath': {'temp': 9.3, 'rain': 2.3, 'temp_var': 5.1, 'rain_var': 1.0},
        'Tipperary': {'temp': 9.6, 'rain': 2.5, 'temp_var': 5.3, 'rain_var': 1.1},
        'Donegal': {'temp': 8.1, 'rain': 3.2, 'temp_var': 4.1, 'rain_var': 1.5},
        'Wexford': {'temp': 9.7, 'rain': 2.6, 'temp_var': 4.9, 'rain_var': 1.2},
        'Roscommon': {'temp': 8.8, 'rain': 2.7, 'temp_var': 4.8, 'rain_var': 1.3}
    }
    
    # Create a date range from 2015 to 2022 with 6-hour steps
    start_date = pd.Timestamp('2015-01-01')
    end_date = pd.Timestamp('2022-12-31 23:59:59')
    
    # Generate 6-hour intervals for sample data
    date_range = pd.date_range(start=start_date, end=end_date, freq='6H')
    
    data = []
    
    # Generate data for each county and date
    for county in counties:
        baseline = county_baselines.get(county, {'temp': 9.0, 'rain': 2.5, 'temp_var': 5.0, 'rain_var': 1.2})
        
        for date in date_range:
            # Apply seasonal adjustments based on month
            month = date.month
            if month in [12, 1, 2]:  # Winter
                season_temp_adj = -2.0
                season_rain_adj = 1.2
            elif month in [3, 4, 5]:  # Spring
                season_temp_adj = 1.0
                season_rain_adj = 0.8
            elif month in [6, 7, 8]:  # Summer
                season_temp_adj = 4.0
                season_rain_adj = 0.6
            else:  # Autumn
                season_temp_adj = 0.0
                season_rain_adj = 1.0
            
            # Apply year-to-year variations (slight warming trend)
            year_adj = (date.year - 2015) * 0.03
            
            # Calculate temperature with seasonal adjustments
            base_temp = baseline['temp'] + season_temp_adj + year_adj
            
            # Add random variation
            temp_variation = np.random.normal(0, baseline['temp_var'] * 0.15)
            rain_variation = np.random.exponential(baseline['rain_var'] * 0.25)
            
            # Calculate final values
            temp = round(base_temp + temp_variation, 2)
            rain = round((baseline['rain'] * season_rain_adj + rain_variation) / 4, 2)  # Divide by 4 for 6-hour intervals
            
            # Create data entry
            data.append({
                'date': date,
                'county': county,
                'temp': temp,
                'rain': rain
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create additional date fields
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    
    # Save to CSV for future use
    df.to_csv('counties_with_data_2015_2022.csv', index=False, date_format='%d-%m-%Y %H:%M')
    
    return df
