import requests
import os
from datetime import datetime
import streamlit as st

# OpenWeatherMap API key
# Get from environment variable or use a default key
API_KEY = os.getenv("OPENWEATHER_API_KEY", "b76ab9b14abba7b3a9a6f86d5c021414")
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
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Use metric units (Celsius)
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        print(response)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

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
