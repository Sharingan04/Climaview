from datetime import datetime

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
