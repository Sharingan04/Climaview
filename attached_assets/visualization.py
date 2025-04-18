import streamlit as st
from datetime import datetime
from utils import format_date, get_weather_icon

def create_weather_dashboard(weather_data):
    """Create a dashboard with current weather information.
    
    Args:
        weather_data (dict): Current weather data
    """
    # Top row with main weather info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"### {weather_data['city']}, {weather_data['country']}")
        st.markdown(f"*{format_date(weather_data['timestamp'])}*")
        st.markdown(f"**{weather_data['weather_main']}** - {weather_data['weather_description']}")
        
    with col2:
        weather_icon = get_weather_icon(weather_data['weather_main'])
        st.markdown(f"<h1 style='text-align: center;'>{weather_icon}</h1>", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"<h2 style='text-align: center;'>{weather_data['temperature']}°C</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Feels like: {weather_data['feels_like']}°C</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Min: {weather_data['temp_min']}°C / Max: {weather_data['temp_max']}°C</p>", unsafe_allow_html=True)
        
    # Second row with additional metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Humidity", f"{weather_data['humidity']}%")
        
    with col2:
        st.metric("Pressure", f"{weather_data['pressure']} hPa")
        
    with col3:
        st.metric("Wind Speed", f"{weather_data['wind_speed']} m/s")
        
    with col4:
        st.metric("Cloud Cover", f"{weather_data['clouds']}%")
