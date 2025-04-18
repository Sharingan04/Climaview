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
    Display the Ireland County Forecast page with visualizations and forecasts.
    """
    st.header("Ireland County Weather Analysis & Forecast")
    
    # Load Irish county weather data
    with st.spinner("Loading Irish weather data..."):
        ireland_df = load_ireland_weather_data()
    
    if ireland_df is None or ireland_df.empty:
        st.error("Failed to load Ireland weather data. Please check that the data file exists.")
        return
    
    # Sidebar for user selections
    st.sidebar.header("Options")
    
    # Get unique counties and years from the dataset
    counties = sorted(ireland_df['county'].unique().tolist())
    years = sorted(ireland_df['year'].unique().tolist())
    
    # User can select multiple counties to compare
    selected_counties = st.sidebar.multiselect(
        "Select Counties to Compare", 
        counties, 
        default=counties[:3]  # Default to first 3 counties
    )
    
    # Year and month selection 
    selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)  # Default to latest year
    
    # Option to filter by month
    show_by_month = st.sidebar.checkbox("Filter by Month")
    if show_by_month:
        selected_month = st.sidebar.slider("Select Month", 1, 12, 6)  # Default to June
    else:
        selected_month = None
    
    # Data exploration header
    st.subheader("Historical Weather Data Exploration")
    
    # Check if counties are selected
    if not selected_counties:
        st.warning("Please select at least one county to display data.")
        return
    
    # Temperature visualization
    st.markdown("### Temperature Trends")
    temp_fig = plot_temperature_by_county(ireland_df, selected_counties, selected_year, selected_month)
    st.plotly_chart(temp_fig, use_container_width=True)
    
    # Rainfall visualization 
    st.markdown("### Rainfall Patterns")
    rain_fig = plot_rainfall_by_county(ireland_df, selected_counties, selected_year, selected_month)
    st.plotly_chart(rain_fig, use_container_width=True)
    
    # Detailed county analysis
    st.subheader("County-Specific Analysis")
    
    # County selection for detailed analysis
    detailed_county = st.selectbox(
        "Select a county for detailed analysis",
        counties
    )
    
    # Create a row with two charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature heatmap
        temp_heatmap = create_temperature_heatmap(ireland_df, detailed_county, selected_year)
        st.plotly_chart(temp_heatmap, use_container_width=True)
    
    with col2:
        # County comparison
        comparison_metric = st.radio(
            "Select metric to compare",
            ["Temperature", "Rainfall"],
            horizontal=True
        )
        metric = 'temp' if comparison_metric == "Temperature" else 'rain'
        
        if not selected_counties:
            st.warning("Please select counties to compare in the sidebar.")
        else:
            comparison_fig = create_county_comparison_chart(ireland_df, selected_counties, selected_year, metric)
            st.plotly_chart(comparison_fig, use_container_width=True)
    
    # Weather forecast section
    st.subheader("Weather Forecast")
    
    # Get the forecast date range
    current_date = datetime.now()
    forecast_days = st.slider("Forecast Days", 1, 7, 3)
    
    # County selection for forecast
    forecast_county = st.selectbox(
        "Select a county for weather forecast",
        counties,
        key="forecast_county"
    )
    
    # Generate forecast when button is clicked
    if st.button("Generate Forecast"):
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
                    temp_metrics_cols = st.columns(min(forecast_days, 7))
                    
                    for i, col in enumerate(temp_metrics_cols):
                        if i < len(forecast_data):
                            day_data = forecast_data.iloc[i]
                            with col:
                                date_str = day_data['date'].strftime('%a, %b %d')
                                st.metric(
                                    label=date_str,
                                    value=f"{day_data['temp']:.1f}°C",
                                    delta=f"{day_data['temp'] - county_data['temp'].mean():.1f}°C"
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
                    rain_metrics_cols = st.columns(min(forecast_days, 7))
                    
                    for i, col in enumerate(rain_metrics_cols):
                        if i < len(forecast_data):
                            day_data = forecast_data.iloc[i]
                            with col:
                                date_str = day_data['date'].strftime('%a, %b %d')
                                st.metric(
                                    label=date_str,
                                    value=f"{day_data['rain']:.2f} mm",
                                    delta=f"{day_data['rain'] - county_data['rain'].mean():.2f} mm"
                                )
            else:
                st.error("Failed to generate forecast. Please try again.")
    
    # Information about the data source
    st.markdown("---")
    st.markdown("""
    #### About the Data
    This data includes historical weather information for Irish counties from 2015-2022, 
    with temperature and rainfall measurements taken at 6-hour intervals.
    
    The forecast is generated using machine learning models trained on this historical data.
    """)
