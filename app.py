import streamlit as st
from datetime import datetime

# Import custom modules
from weather_api import get_current_weather, get_city_suggestions
from visualization import create_weather_dashboard
from utils import format_weather_data
from ireland_forecast import display_ireland_forecast_page
import bicycle_analysis

# Page configuration
st.set_page_config(
    page_title="WeatherWise",
    page_icon="🌤️",
    layout="wide"
)

# Title 
st.title("☁️The Weather Dashboard")

# Create tabs for different features
tab1, tab2, tab3= st.tabs(["Global Weather", "Ireland County Forecast", "Dublin Climate vs Bicycle Analysis"])

with tab1:
    st.markdown("""
    Enter a city name below to get started!
    """)

with tab1:
    # Session state initialization
    if 'city' not in st.session_state:
        st.session_state.city = ""
    if 'last_search' not in st.session_state:
        st.session_state.last_search = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

    # City search with autocomplete
    city_input = st.text_input(
        "Enter city name:",
        key="city_input",
        value=st.session_state.city
    )

    # Autocomplete suggestions
    if city_input and city_input != st.session_state.city:
        suggestions = get_city_suggestions(city_input)
        if suggestions:
            selected_city = st.selectbox(
                "Did you mean?",
                options=suggestions,
                index=0 if suggestions else None
            )
            if st.button("Use this city"):
                st.session_state.city = selected_city
                st.rerun()
        
    # Search button
    search_col, clear_col = st.columns([1, 1])
    with search_col:
        search_clicked = st.button("Search Weather", type="primary")
    with clear_col:
        clear_clicked = st.button("Clear Results")

    # Process the search
    if search_clicked and city_input:
        st.session_state.city = city_input
        # Show a spinner while loading data
        with st.spinner(f"Fetching weather data for {st.session_state.city}..."):
            # Get current weather information
            weather_data = get_current_weather(st.session_state.city)
            
            if weather_data and 'cod' in weather_data:
                if weather_data['cod'] == 200:
                    # Add to search history if not already there
                    if st.session_state.city not in st.session_state.search_history:
                        st.session_state.search_history.insert(0, st.session_state.city)
                        # Keep only the last 5 searches
                        st.session_state.search_history = st.session_state.search_history[:5]
                    
                    # Format weather data for display
                    formatted_data = format_weather_data(weather_data)
                    
                    # Update last search time
                    st.session_state.last_search = datetime.now()
                else:
                    # Display the specific error message from the API
                    error_message = weather_data.get('message', 'Unknown error')
                    st.error(f"Error fetching weather data: {error_message}")
                    st.info(f"Please check if '{st.session_state.city}' is a valid city name and try again.")
            else:
                st.error(f"Unable to fetch weather data for {st.session_state.city}. Please check the city name and try again.")

    # Clear results
    if clear_clicked:
        st.session_state.city = ""
        st.session_state.last_search = None
        st.rerun()

    # Display search history as clickable chips
    if st.session_state.search_history:
        st.write("Recent searches:")
        history_cols = st.columns(len(st.session_state.search_history))
        for i, city in enumerate(st.session_state.search_history):
            with history_cols[i]:
                if st.button(city, key=f"history_{i}"):
                    st.session_state.city = city
                    st.rerun()

    # Display the current weather if a city is selected
    if st.session_state.city and st.session_state.last_search:
        weather_data = get_current_weather(st.session_state.city)
        
        if weather_data and 'cod' in weather_data:
            if weather_data['cod'] == 200:
                # Display current weather information
                st.header(f"Current Weather in {st.session_state.city}")
                
                # Format the data
                formatted_data = format_weather_data(weather_data)
                
                # Create dashboard with current weather
                create_weather_dashboard(formatted_data)
            else:
                # Display the specific error message from the API
                error_message = weather_data.get('message', 'Unknown error')
                st.error(f"Error fetching weather data: {error_message}")
                st.info(f"Please check if '{st.session_state.city}' is a valid city name and try again.")
        else:
            st.error(f"Unable to fetch weather data for {st.session_state.city}. Please check the city name and try again.")

# Display the Ireland County Forecast tab
with tab2:
    display_ireland_forecast_page()

with tab3:
    bicycle_analysis.render_bicycle_analysis_tab()
# Footer
st.markdown("---")

