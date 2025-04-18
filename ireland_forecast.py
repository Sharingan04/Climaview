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
    st.header("Ireland County Weather Forecast")
    
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
    The forecasts are based on historical weather patterns and current conditions.
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
                forecast_tab1, forecast_tab2 = st.tabs(["Temperature Forecast", "Rainfall Forecast"])
                
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
            else:
                st.error("Failed to generate forecast. Please try again.")
    
    # Information about the data source
    st.markdown("---")
    st.markdown("""
    #### About the Forecast
    The weather forecast is based on historical weather patterns and current conditions for Irish counties.
    The data includes forecast information for temperature and rainfall for the next 5 days.
    
    This forecast uses accurate weather models based on historical data and meteorological predictions.
    """)
