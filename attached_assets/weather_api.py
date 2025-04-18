import requests
import os
from datetime import datetime
import streamlit as st

# OpenWeatherMap API key
# Get from environment variable
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Check if API key is available
if not API_KEY:
    import streamlit as st
    st.error("⚠️ OpenWeatherMap API key is missing. Please add it to the secrets.")
    st.info("Without a valid API key, the weather data cannot be fetched.")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

# Cache API responses to reduce API calls
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_current_weather(city):
    """Get current weather data for a city.
    
    Args:
        city (str): City name
        
    Returns:
        dict: Weather data from OpenWeatherMap API
    """
    # Prepare city name properly (trim whitespace, etc.)
    city = city.strip()
    
    if not city:
        return {"cod": 400, "message": "City name cannot be empty"}
    
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Use metric units (Celsius)
    }
    
    try:
        # For debugging, uncomment the line below
        # print(f"Fetching weather data for: {city}")
        
        response = requests.get(BASE_URL, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            # Log the error response for debugging
            error_data = response.json()
            st.error(f"API Error: {error_data.get('message', 'Unknown error')}", key="api_error")
            return {"cod": response.status_code, "message": error_data.get('message', 'Unknown error')}
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching weather data: {e}", key="network_error")
        return {"cod": 500, "message": f"Network error: {str(e)}"}
    except Exception as e:
        st.error(f"Unexpected error: {e}", key="unexpected_error")
        return {"cod": 500, "message": f"Unexpected error: {str(e)}"}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_city_coordinates(city):
    """Get latitude and longitude for a city.
    
    Args:
        city (str): City name
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    params = {
        'q': city,
        'appid': API_KEY,
        'limit': 1
    }
    
    try:
        response = requests.get(GEO_URL, params=params)
        data = response.json()
        
        if data and len(data) > 0:
            return data[0]['lat'], data[0]['lon']
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching city coordinates: {e}")
        return None, None

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_city_suggestions(query):
    """Get city suggestions based on partial input.
    
    Args:
        query (str): Partial city name
        
    Returns:
        list: List of city name suggestions
    """
    if not query or len(query) < 3:
        return []
    
    params = {
        'q': query,
        'appid': API_KEY,
        'limit': 5
    }
    
    try:
        response = requests.get(GEO_URL, params=params)
        data = response.json()
        
        suggestions = []
        if isinstance(data, list):  # Make sure data is a list
            for item in data:
                if isinstance(item, dict) and 'name' in item:  # Make sure item is a dictionary
                    city_name = item['name']
                    if 'state' in item and item['state']:
                        city_name += f", {item['state']}"
                    if 'country' in item:
                        city_name += f", {item['country']}"
                    suggestions.append(city_name)
        
        return suggestions
    except (requests.exceptions.RequestException, TypeError, ValueError) as e:
        st.error(f"Error fetching city suggestions: {e}")
        return []
