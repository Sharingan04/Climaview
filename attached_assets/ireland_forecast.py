import pandas as pd
import requests
import streamlit as st
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from irish_weather_scraper import scrape_met_eireann_data, get_county_data, get_forecast_data

# Use the same API key as the main app
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Dictionary of Irish counties with their coordinates
COUNTIES = {
    'Dublin': (53.3498, -6.2603),
    'Galway': (53.2707, -9.0568),
    'Carlow': (52.8365, -6.9341),
    'Clare': (52.8436, -9.0031),
    'Cork': (51.8985, -8.4756),
    'Cavan': (53.9908, -7.3606),
    'Westmeath': (53.5333, -7.3667),
    'Mayo': (53.7667, -9.5000),
    'Sligo': (54.2706, -8.4716),
    'Meath': (53.6050, -6.6556),
    'Tipperary': (52.4735, -8.1618),
    'Donegal': (54.6542, -8.1096),
    'Wexford': (52.3365, -6.4629),
    'Roscommon': (53.6333, -8.1833)
}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_weather(lat, lon):
    """Get current weather for given coordinates."""
    if not API_KEY:
        st.warning("No API key available, using simulated weather data for demonstration")
        # Return simulated data for demonstration
        return {
            'temp': 15 + (lat % 5),  # Simulated temperature between 10-20°C
            'rain': round(1.0 + (lon % 3), 2)  # Simulated rainfall between 0-3mm
        }
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'rain': data.get('rain', {}).get('1h', 0.0)  # mm in last hour
            }
        else:
            st.error(f"Error fetching data: {response.json().get('message', 'Unknown error')}")
            # Fallback to simulated data
            st.warning("Using simulated weather data for demonstration")
            return {
                'temp': 15 + (lat % 5),  # Simulated temperature between 10-20°C
                'rain': round(1.0 + (lon % 3), 2)  # Simulated rainfall between 0-3mm
            }
    except Exception as e:
        st.error(f"Error connecting to weather API: {str(e)}")
        # Fallback to simulated data
        st.warning("Using simulated weather data for demonstration")
        return {
            'temp': 15 + (lat % 5),  # Simulated temperature between 10-20°C
            'rain': round(1.0 + (lon % 3), 2)  # Simulated rainfall between 0-3mm
        }

def generate_historical_data_to_2025(county):
    """Generate historical weather data for a county up to January 1, 2025.
    
    This simulates a dataset that would typically come from a database or API.
    """
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
    
    # Get baseline values for the county or use default
    baseline = county_baselines.get(county, {'temp': 9.0, 'rain': 2.5, 'temp_var': 5.0, 'rain_var': 1.2})
    
    # Generate monthly average data for 2023-2024
    months = []
    temps = []
    rains = []
    
    # Generate data for Jan 2023 to Jan 2025
    for year in [2023, 2024]:
        for month in range(1, 13):
            # Handle seasonality
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
            
            # Calculate temperature and rainfall with seasonal adjustment
            temp = round(baseline['temp'] + season_temp_adj, 2)
            rain = round(baseline['rain'] * season_rain_adj, 2)
            
            months.append(f"{year}-{month:02d}")
            temps.append(temp)
            rains.append(rain)
    
    # Add January 2025
    months.append("2025-01")
    temps.append(round(baseline['temp'] - 2.0, 2))  # Winter adjustment
    rains.append(round(baseline['rain'] * 1.2, 2))  # Winter adjustment
    
    return months, temps, rains

def generate_forecast_for_county(county, today_weather, days=5):
    """Generate a 5-day forecast for the given county based on historical trends.
    
    This uses simulated historical data up to January 1, 2025,
    and then forecasts from that point forward.
    """
    if today_weather['temp'] is None or today_weather['rain'] is None:
        return None
    
    # Get historical data
    months, temps, rains = generate_historical_data_to_2025(county)
    
    # Use the latest historical data as a starting point
    base_temp = temps[-1]
    base_rain = rains[-1]
    
    # Seasonal adjustment factors for different counties in January
    county_factors = {
        'Dublin': {'temp_change': 0.01, 'rain_change': 0.05},
        'Galway': {'temp_change': 0.03, 'rain_change': 0.02},
        'Carlow': {'temp_change': 0.00, 'rain_change': 0.07},
        'Clare': {'temp_change': 0.02, 'rain_change': 0.05},
        'Cork': {'temp_change': -0.01, 'rain_change': 0.10},
        'Cavan': {'temp_change': 0.01, 'rain_change': 0.05},
        'Westmeath': {'temp_change': 0.01, 'rain_change': 0.07},
        'Mayo': {'temp_change': 0.02, 'rain_change': 0.08},
        'Sligo': {'temp_change': 0.03, 'rain_change': 0.00},
        'Meath': {'temp_change': 0.01, 'rain_change': 0.05},
        'Tipperary': {'temp_change': -0.01, 'rain_change': 0.04},
        'Donegal': {'temp_change': 0.02, 'rain_change': -0.04},
        'Wexford': {'temp_change': 0.00, 'rain_change': 0.06},
        'Roscommon': {'temp_change': 0.01, 'rain_change': 0.05}
    }
    
    factors = county_factors.get(county, {'temp_change': 0.01, 'rain_change': 0.05})
    
    # Generate forecasts for the next 'days' days starting from January 1, 2025
    temperature_forecast = []
    rainfall_forecast = []
    
    for i in range(1, days+1):
        # Calculate forecast with slight daily variations
        day_var_temp = (i % 2) * 0.2 - 0.1  # Small oscillation between -0.1 and 0.1
        day_var_rain = (i % 3) * 0.1        # Small increase every 3 days
        
        temp = round(base_temp + (i * factors['temp_change'] * base_temp) + day_var_temp, 2)
        rain = round(base_rain + (i * factors['rain_change'] * base_rain) + day_var_rain, 2)
        
        temperature_forecast.append(temp)
        rainfall_forecast.append(rain)
    
    return {
        'temperature_next_5_days': temperature_forecast,
        'rainfall_next_5_days': rainfall_forecast,
        'historical_months': months,
        'historical_temps': temps,
        'historical_rains': rains
    }

def get_all_county_forecasts():
    """Generate forecasts for all counties in Ireland."""
    today = datetime.now().date()
    forecasts = {}
    
    for county, (lat, lon) in COUNTIES.items():
        with st.spinner(f"Fetching data for {county}..."):
            today_weather = get_weather(lat, lon)
            forecast = generate_forecast_for_county(county, today_weather)
            if forecast:
                forecasts[county] = forecast
    
    return forecasts, today

def display_county_forecast(county, forecast, today):
    """Display a forecast for a single county."""
    st.header(f"📍 Forecast for {county} (Starting January 1, 2025)")
    
    if not forecast:
        st.warning("Forecast data is not available for this county.")
        return
    
    # Display forecast data with tabs
    forecast_tab, historical_tab = st.tabs(["5-Day Forecast", "Historical Data (2015-2025)"])
    
    with forecast_tab:
        # Create or update the forecast DataFrame
        if 'weather_descriptions' in forecast:
            # Use the descriptions provided in the forecast
            forecast_df = pd.DataFrame({
                'Day': [f"Day +{i+1}" for i in range(5)],
                'Date': forecast.get('forecast_dates', [''] * 5),
                'Temperature (°C)': forecast['temperature_next_5_days'],
                'Rainfall (mm)': forecast['rainfall_next_5_days'],
                'Weather': forecast['weather_descriptions']
            })
        else:
            # If no descriptions provided, get them now
            from irish_weather_scraper import get_weather_description
            
            days = [f"Day +{i+1}" for i in range(5)]
            dates = [f"Jan {i+2}, 2025" for i in range(5)]  # Placeholder dates
            descriptions = []
            
            for i in range(5):
                temp = forecast['temperature_next_5_days'][i]
                rain = forecast['rainfall_next_5_days'][i]
                descriptions.append(get_weather_description(temp, rain))
            
            forecast_df = pd.DataFrame({
                'Day': days,
                'Date': dates,
                'Temperature (°C)': forecast['temperature_next_5_days'],
                'Rainfall (mm)': forecast['rainfall_next_5_days'],
                'Weather': descriptions
            })
        
        # Display the forecast as a table
        st.subheader(f"5-Day Weather Forecast (from Jan 1, 2025)")
        st.dataframe(forecast_df, use_container_width=True)
        
        # Display the first day's forecast as a featured card
        if len(forecast_df) > 0:
            st.subheader("Tomorrow's Forecast")
            col1, col2 = st.columns([1, 2])
            with col1:
                # Temperature icon based on the value
                temp = forecast_df['Temperature (°C)'].iloc[0]
                if temp < 5:
                    temp_icon = "❄️"
                elif temp < 10:
                    temp_icon = "🌤️"
                elif temp < 15:
                    temp_icon = "☀️"
                elif temp < 20:
                    temp_icon = "☀️"
                else:
                    temp_icon = "🔥"
                
                # Rain icon based on the value
                rain = forecast_df['Rainfall (mm)'].iloc[0]
                if rain < 0.5:
                    rain_icon = "☀️"
                elif rain < 1.5:
                    rain_icon = "⛅"
                elif rain < 3:
                    rain_icon = "🌦️"
                elif rain < 5:
                    rain_icon = "🌧️"
                else:
                    rain_icon = "⛈️"
                
                # Display temperature and rainfall with icons
                st.metric("Temperature", f"{temp}°C", delta=None, delta_color="normal")
                st.metric("Rainfall", f"{rain} mm", delta=None, delta_color="normal")
            
            with col2:
                # Display the weather description in a card-like container
                weather_desc = forecast_df['Weather'].iloc[0]
                date_str = forecast_df['Date'].iloc[0]
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
                    <h3 style="margin-top: 0;">{date_str}</h3>
                    <p style="font-size: 1.2em; margin-bottom: 0;">{weather_desc}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Create tabs for Temperature and Rainfall charts
        temp_tab, rain_tab = st.tabs(["Temperature Forecast", "Rainfall Forecast"])
        
        with temp_tab:
            fig_temp = px.line(
                forecast_df, 
                x='Day', 
                y='Temperature (°C)',
                markers=True,
                line_shape='linear',
                title=f"Temperature Forecast for {county}"
            )
            fig_temp.update_traces(line=dict(color="#FF9500", width=3), marker=dict(size=10))
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with rain_tab:
            fig_rain = px.bar(
                forecast_df,
                x='Day',
                y='Rainfall (mm)',
                title=f"Rainfall Forecast for {county}"
            )
            fig_rain.update_traces(marker=dict(color="#3498DB"))
            st.plotly_chart(fig_rain, use_container_width=True)
    
    with historical_tab:
        st.subheader(f"Historical Weather Data (2015-2025)")
        
        # Create historical dataframe
        historical_df = pd.DataFrame({
            'Date': forecast['historical_months'],
            'Temperature (°C)': forecast['historical_temps'],
            'Rainfall (mm)': forecast['historical_rains']
        })
        
        # Display summary statistics
        st.write("Summary Statistics:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Temperature", f"{historical_df['Temperature (°C)'].mean():.1f}°C")
        with col2:
            st.metric("Average Rainfall", f"{historical_df['Rainfall (mm)'].mean():.1f} mm")
        with col3:
            st.metric("Data Points", f"{len(historical_df)} months")
        
        # Add a filter for year range
        st.write("Filter historical data:")
        # Extract years from dates
        if len(historical_df) > 0:
            # Show option to filter by year
            all_years = sorted(list(set([int(date.split('-')[0]) for date in historical_df['Date']])))
            selected_years = st.multiselect(
                "Select years to display:", 
                options=all_years,
                default=all_years[-3:]  # Default to last 3 years
            )
            
            if selected_years:
                filtered_df = historical_df[historical_df['Date'].apply(lambda x: int(x.split('-')[0]) in selected_years)]
            else:
                filtered_df = historical_df
            
            # Display the filtered historical data as a table
            st.dataframe(filtered_df, use_container_width=True)
            
            # Create historical charts
            hist_temp_tab, hist_rain_tab, yearly_analysis_tab = st.tabs([
                "Temperature Trends", "Rainfall Trends", "Yearly Analysis"
            ])
            
            with hist_temp_tab:
                fig_hist_temp = px.line(
                    filtered_df,
                    x='Date',
                    y='Temperature (°C)',
                    markers=True,
                    title=f"Historical Temperature Data for {county} ({', '.join(map(str, selected_years))})"
                )
                fig_hist_temp.update_traces(line=dict(color="#FF9500", width=2), marker=dict(size=6))
                
                # Highlight January 2025 if it's in the selected years
                if 2025 in selected_years:
                    # Find the January 2025 entry
                    jan_2025_entries = filtered_df[filtered_df['Date'].str.startswith('2025-01')]
                    if not jan_2025_entries.empty:
                        fig_hist_temp.add_scatter(
                            x=jan_2025_entries['Date'].tolist(),
                            y=jan_2025_entries['Temperature (°C)'].tolist(),
                            mode='markers',
                            marker=dict(color='red', size=12, symbol='star'),
                            name='January 2025'
                        )
                
                fig_hist_temp.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_hist_temp, use_container_width=True)
            
            with hist_rain_tab:
                fig_hist_rain = px.bar(
                    filtered_df,
                    x='Date',
                    y='Rainfall (mm)',
                    title=f"Historical Rainfall Data for {county} ({', '.join(map(str, selected_years))})"
                )
                fig_hist_rain.update_traces(marker=dict(color="#3498DB"))
                
                # Highlight January 2025 if it's in the selected years
                if 2025 in selected_years:
                    # Find the January 2025 entry
                    jan_2025_entries = filtered_df[filtered_df['Date'].str.startswith('2025-01')]
                    if not jan_2025_entries.empty:
                        fig_hist_rain.add_scatter(
                            x=jan_2025_entries['Date'].tolist(),
                            y=jan_2025_entries['Rainfall (mm)'].tolist(),
                            mode='markers',
                            marker=dict(color='red', size=12, symbol='star'),
                            name='January 2025'
                        )
                
                fig_hist_rain.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_hist_rain, use_container_width=True)
                
            with yearly_analysis_tab:
                # Calculate yearly averages
                yearly_data = []
                for year in all_years:
                    year_data = historical_df[historical_df['Date'].apply(lambda x: int(x.split('-')[0]) == year)]
                    if not year_data.empty:
                        yearly_data.append({
                            'Year': year,
                            'Avg Temperature (°C)': year_data['Temperature (°C)'].mean(),
                            'Avg Rainfall (mm)': year_data['Rainfall (mm)'].mean(),
                            'Total Rainfall (mm)': year_data['Rainfall (mm)'].sum()
                        })
                
                yearly_df = pd.DataFrame(yearly_data)
                
                # Display yearly trends
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_yearly_temp = px.line(
                        yearly_df, 
                        x='Year', 
                        y='Avg Temperature (°C)',
                        markers=True,
                        title=f"Yearly Average Temperature ({county})"
                    )
                    fig_yearly_temp.update_traces(line=dict(color="#FF9500", width=2), marker=dict(size=8))
                    st.plotly_chart(fig_yearly_temp, use_container_width=True)
                
                with col2:
                    fig_yearly_rain = px.line(
                        yearly_df, 
                        x='Year', 
                        y='Total Rainfall (mm)',
                        markers=True,
                        title=f"Yearly Total Rainfall ({county})"
                    )
                    fig_yearly_rain.update_traces(line=dict(color="#3498DB", width=2), marker=dict(size=8))
                    st.plotly_chart(fig_yearly_rain, use_container_width=True)
                
                # Display yearly summary table
                st.subheader("Yearly Summary")
                st.dataframe(yearly_df, use_container_width=True)

def display_ireland_forecast_page():
    """Display the Ireland forecast page in the app."""
    st.title("🍀 Ireland County Weather Forecast")
    st.markdown("""
    This page provides historical weather data (2015-2025) and 5-day forecasts for counties in Ireland.
    The data is sourced from the Met Éireann (Irish Meteorological Service) and covers a comprehensive
    period from 2015 up to January 2025, with a 5-day forecast starting from January 1, 2025.
    
    Select a county from the dropdown to view its historical data and forecast.
    """)
    
    # Fetch Irish weather data from Met Éireann
    with st.spinner("Loading Irish weather data from 2015-2025..."):
        irish_weather_data = scrape_met_eireann_data()
    
    if irish_weather_data is None:
        st.error("Failed to load Irish weather data. Please try again later.")
        return
        
    # County selector
    county = st.selectbox(
        "Select a county:",
        options=sorted(COUNTIES.keys()),
        index=0
    )
    
    if st.button("Get Forecast", type="primary"):
        with st.spinner(f"Generating weather forecast for {county}..."):
            # Extract county-specific data
            county_data = get_county_data(irish_weather_data, county)
            
            if county_data is None or county_data.empty:
                st.error(f"No data available for {county}. Please select another county.")
                return
                
            # Get 5-day forecast starting from Jan 1, 2025
            forecast_data = get_forecast_data(county_data)
            
            if forecast_data is None:
                st.error(f"Unable to generate forecast for {county}. Please try again later.")
                return
                
            # Create a forecast object compatible with our display function
            latest_data = county_data.iloc[-1]
            
            # Format historical data for display
            # Get all data from 2015-2025
            historical_df = county_data.copy()
            historical_df['date'] = historical_df['date']
            
            # Create forecast object with weather descriptions
            forecast = {
                'temperature_next_5_days': forecast_data['temperature'].tolist(),
                'rainfall_next_5_days': forecast_data['rainfall'].tolist(),
                'weather_descriptions': forecast_data['description'].tolist(),
                'forecast_dates': forecast_data['date'].tolist(),
                'historical_months': historical_df['date'].tolist(),
                'historical_temps': historical_df['temperature'].tolist(),
                'historical_rains': historical_df['rainfall'].tolist()
            }
            
            today = datetime.now().date()
            
            # Display the forecast and historical data
            display_county_forecast(county, forecast, today)
            
            # Add explanation about the data source
            st.info("This data is sourced from Met Éireann (Irish Meteorological Service) historical records from 2015-2025.")