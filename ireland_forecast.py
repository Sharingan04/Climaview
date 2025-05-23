import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from utils import load_ireland_weather_data
from visualization import (
    plot_temperature_by_county,
    plot_rainfall_by_county,
    create_temperature_heatmap,
    create_county_comparison_chart
)
from ml_forecast import predict_county_weather

def display_ireland_forecast_page():
    """
    Display the Ireland County Forecast page with forecasts only.
    """
    st.header("Ireland Countywise Weather Forecast")
    
    # Load Irish county weather data
    with st.spinner("Loading Irish weather data..."):
        ireland_df = load_ireland_weather_data()
    
    if ireland_df is None or ireland_df.empty:
        st.error("Failed to load Ireland weather data. Please check that the data file exists.")
        return
    
    # Get unique counties from the dataset
    counties = sorted(ireland_df['county'].unique().tolist())
    
    # Weather forecast section
    st.subheader("5-Day Weather Forecast")
    
    st.markdown("""
    Select a county below to view its 5-day weather forecast. 
    """)
    
    # Get the forecast date range
    current_date = datetime.now()
    forecast_days = st.slider("Forecast Days", 1, 5, 5)
    
    # County selection for forecast
    forecast_county = st.selectbox(
        "Select a county",
        counties,
        key="forecast_county"
    )
    
    # Generate forecast when button is clicked
    if st.button("Generate Forecast", type="primary"):
        with st.spinner(f"Generating forecast for {forecast_county}..."):
            # Get historical data for the selected county
            county_data = ireland_df[ireland_df['county'] == forecast_county].copy()
            
            # Generate forecast using ML model
            forecast_data = predict_county_weather(county_data, forecast_days)
            
            if forecast_data is not None:
                # Display forecast results
                st.markdown(f"### {forecast_days}-Day Forecast for {forecast_county}")
                
                # Create tabs for different forecast views
                forecast_tab1, forecast_tab2, forecast_tab3 = st.tabs([
                    "Temperature Forecast", 
                    "Rainfall Forecast",
                    "Humidity Forecast"
                ])
                
                # Temperature tab
                with forecast_tab1:
                    # Temperature forecast chart
                    temp_forecast_fig = px.line(
                        forecast_data,
                        x='date',
                        y='temp',
                        title=f'Temperature Forecast for {forecast_county}',
                        labels={'temp': 'Temperature (°C)', 'date': 'Date'}
                    )
                    
                    temp_forecast_fig.update_layout(
                        hovermode='x unified',
                        showlegend=False
                    )
                    
                    # Add confidence interval
                    temp_forecast_fig.add_traces([
                        go.Scatter(
                            name='Upper Bound',
                            x=forecast_data['date'],
                            y=forecast_data['temp_upper'],
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False
                        ),
                        go.Scatter(
                            name='Lower Bound',
                            x=forecast_data['date'],
                            y=forecast_data['temp_lower'],
                            mode='lines',
                            line=dict(width=0),
                            fill='tonexty',
                            fillcolor='rgba(68, 68, 68, 0.2)',
                            showlegend=False
                        )
                    ])
                    
                    st.plotly_chart(temp_forecast_fig, use_container_width=True)
                    
                    # Daily temperature metrics
                    st.markdown("#### Daily Temperature Forecast")
                    temp_metrics_cols = st.columns(min(forecast_days, 5))
                    
                    for i, col in enumerate(temp_metrics_cols):
                        if i < len(forecast_data):
                            day_data = forecast_data.iloc[i]
                            with col:
                                date_str = day_data['date'].strftime('%a, %b %d')
                                st.metric(
                                    label=date_str,
                                    value=f"{day_data['temp']:.1f}°C",
                                    delta=None
                                )
                
                # Rainfall tab
                with forecast_tab2:
                    # Rainfall forecast chart
                    rain_forecast_fig = px.bar(
                        forecast_data,
                        x='date',
                        y='rain',
                        title=f'Rainfall Forecast for {forecast_county}',
                        labels={'rain': 'Rainfall (mm)', 'date': 'Date'}
                    )
                    
                    rain_forecast_fig.update_layout(
                        hovermode='x unified',
                        showlegend=False
                    )
                    
                    st.plotly_chart(rain_forecast_fig, use_container_width=True)
                    
                    # Daily rainfall metrics
                    st.markdown("#### Daily Rainfall Forecast")
                    rain_metrics_cols = st.columns(min(forecast_days, 5))
                    
                    for i, col in enumerate(rain_metrics_cols):
                        if i < len(forecast_data):
                            day_data = forecast_data.iloc[i]
                            with col:
                                date_str = day_data['date'].strftime('%a, %b %d')
                                st.metric(
                                    label=date_str,
                                    value=f"{day_data['rain']:.2f} mm",
                                    delta=None
                                )
                
                # Humidity tab
                with forecast_tab3:
                    # Humidity forecast chart
                    humidity_forecast_fig = px.line(
                        forecast_data,
                        x='date',
                        y='humidity',
                        title=f'Humidity Forecast for {forecast_county}',
                        labels={'humidity': 'Relative Humidity (%)', 'date': 'Date'}
                    )
                    
                    humidity_forecast_fig.update_layout(
                        hovermode='x unified',
                        showlegend=False,
                        yaxis=dict(range=[0, 100])  # Humidity scale from 0-100%
                    )
                    
                    st.plotly_chart(humidity_forecast_fig, use_container_width=True)
                    
                    # Daily humidity metrics
                    st.markdown("#### Daily Humidity Forecast")
                    humidity_metrics_cols = st.columns(min(forecast_days, 5))
                    
                    # Define humidity level descriptions
                    def get_humidity_description(humidity):
                        if humidity < 40:
                            return "Dry"
                        elif humidity < 60:
                            return "Comfortable"
                        elif humidity < 75:
                            return "Humid"
                        else:
                            return "Very Humid"
                    
                    for i, col in enumerate(humidity_metrics_cols):
                        if i < len(forecast_data):
                            day_data = forecast_data.iloc[i]
                            with col:
                                date_str = day_data['date'].strftime('%a, %b %d')
                                humidity_value = int(day_data['humidity'])
                                humidity_desc = get_humidity_description(humidity_value)
                                
                                st.metric(
                                    label=date_str,
                                    value=f"{humidity_value}%",
                                    delta=None
                                )
                                st.caption(f"{humidity_desc}")
                
                # Show combined daily forecast
                st.markdown("### Daily Weather Summary")
                
                # Create a daily summary table with all metrics
                summary_data = {
                    'Date': [d.strftime('%a, %b %d') for d in forecast_data['date']],
                    'Temperature (°C)': [f"{t:.1f}" for t in forecast_data['temp']],
                    'Rainfall (mm)': [f"{r:.1f}" for r in forecast_data['rain']],
                    'Humidity (%)': [f"{h}%" for h in forecast_data['humidity']]
                }
                
                st.dataframe(
                    summary_data,
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                st.error("Failed to generate forecast. Please try again.")
