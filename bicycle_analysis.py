import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from Cycle_Stats import load_bicycle_data, get_weather_data, preprocess_data_for_analysis

def render_bicycle_analysis_tab():
    """
    Render the bicycle analysis tab
    """
    st.title("Dublin Bicycle Usage Analysis")
    st.write("Explore the relationship between weather conditions and bicycle usage in Dublin")
    
    # Load data with caching
    @st.cache_data(ttl=3600)
    def load_data():
        bicycle_data = load_bicycle_data()
        weather_data = get_weather_data(city="Dublin")
        return bicycle_data, weather_data
    
    with st.spinner("Loading bicycle and weather data..."):
        bicycle_data, weather_data = load_data()
    
    # Show data loading success message
    st.success(f"Loaded bicycle data with {len(bicycle_data)} records from {bicycle_data['Year'].min()} to {bicycle_data['Year'].max()}")
    
    # Filters directly in the tab instead of sidebar
    st.subheader("Filter Data")
    
    # Use columns for filter layout
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Create a list of years present in the data
        years = sorted(bicycle_data['Year'].unique())
        selected_years = st.multiselect("Select Years", years, default=years)
    
    with filter_col2:
        # Create a list of locations for filtering
        locations = sorted(bicycle_data['Location'].unique())
        selected_locations = st.multiselect("Select Locations", locations, 
                                          default=locations[:5] if len(locations) > 5 else locations)
    
    with filter_col3:
        # Filter for seasons
        seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
        selected_seasons = st.multiselect("Select Seasons", seasons, default=seasons)
        
    # Additional filters with select/dropdown format
    filter_col4, filter_col5 = st.columns(2)
    
    with filter_col4:
        # Weekday filter
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_day = st.selectbox("Select Day of Week (optional)", ['All Days'] + weekdays)
    
    with filter_col5:
        # Time of day filter
        time_periods = ['All Day', 'Morning (6-10)', 'Midday (10-14)', 'Afternoon (14-18)', 'Evening (18-22)', 'Night (22-6)']
        selected_time_period = st.selectbox("Select Time Period", time_periods)
    
    # Apply filters
    filtered_data = bicycle_data[
        (bicycle_data['Year'].isin(selected_years)) &
        (bicycle_data['Location'].isin(selected_locations)) &
        (bicycle_data['Season'].isin(selected_seasons))
    ]
    
    # Apply day of week filter if specific day selected
    if selected_day != 'All Days':
        filtered_data['DayOfWeek'] = pd.to_datetime(filtered_data['Time']).dt.day_name()
        filtered_data = filtered_data[filtered_data['DayOfWeek'] == selected_day]
    
    # Apply time of day filter
    if selected_time_period != 'All Day':
        hour_ranges = {
            'Morning (6-10)': (6, 10),
            'Midday (10-14)': (10, 14),
            'Afternoon (14-18)': (14, 18),
            'Evening (18-22)': (18, 22),
            'Night (22-6)': (22, 6)
        }
        
        # This can now be removed as 2023 data is properly integrated in utils.py
        
        selected_range = hour_ranges[selected_time_period]
        if selected_range[0] < selected_range[1]:  # normal range (e.g., 6-10)
            filtered_data = filtered_data[
                (filtered_data['Hour'] >= selected_range[0]) & 
                (filtered_data['Hour'] < selected_range[1])
            ]
        else:  # overnight range (e.g., 22-6)
            filtered_data = filtered_data[
                (filtered_data['Hour'] >= selected_range[0]) | 
                (filtered_data['Hour'] < selected_range[1])
            ]
    
    # Check if we have data after filtering
    if filtered_data.empty:
        st.warning("No data available with the current filter settings. Please adjust your filters.")
        return
    
    # Data Overview
    st.header("Overview of Bicycle Usage")
    
    # Metrics for bicycle usage
    col1, col2, col3 = st.columns(3)
    with col1:
        total_cyclists = filtered_data['Count'].sum()
        st.metric("Total Cyclists", f"{total_cyclists:,}")
    
    with col2:
        avg_daily = filtered_data.groupby('Date')['Count'].sum().mean()
        st.metric("Avg. Daily Cyclists", f"{int(avg_daily):,}")
    
    with col3:
        # Add a note that we're limiting analysis to 2020-2022
        st.metric("Data Range", "2020-2022", help="Analysis limited to 2020-2022 as per weather data availability")
    
    # Prepare data for analysis
    analyze_btn = st.button("Analyze Weather Correlation")
    
    if analyze_btn:
        with st.spinner("Analyzing bicycle usage patterns..."):
            # Use only the filtered data dates to get relevant weather data
            start_date = filtered_data['Date'].min()
            end_date = filtered_data['Date'].max()
            
            # Get updated weather data if needed
            weather_data = get_weather_data(city="Dublin", start_date=start_date, end_date=end_date)
            
            # Process data for analysis
            analysis_data = preprocess_data_for_analysis(filtered_data, weather_data)
            
            # Visualizations
            st.header("Weather Impact Analysis")
            
            # 1. Bicycle Usage by Temperature
            st.subheader("Bicycle Usage vs. Temperature")
            fig = px.scatter(analysis_data, x='temp_max', y='Total_Cyclists', 
                           title='Correlation between Maximum Temperature and Bicycle Usage',
                           color='precipitation', hover_data=['date'])
            fig.update_layout(xaxis_title='Maximum Temperature (°C)', 
                            yaxis_title='Total Daily Cyclists',
                            coloraxis_colorbar_title='Precipitation (mm)')
            st.plotly_chart(fig, use_container_width=True)
            
            # 2. Bicycle Usage by Precipitation
            st.subheader("Impact of Precipitation on Bicycle Usage")
            fig = px.scatter(analysis_data, x='precipitation', y='Total_Cyclists',
                           title='How Rain Affects Cycling in Dublin',
                           color='temp_max', hover_data=['date'])
            fig.update_layout(xaxis_title='Precipitation (mm)',
                            yaxis_title='Total Daily Cyclists',
                            coloraxis_colorbar_title='Max Temp (°C)')
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. Monthly trends with weather overlay
            st.subheader("Monthly Bicycle Usage Trends")
            # Add month name to analysis data
            analysis_data['Month'] = pd.to_datetime(analysis_data['date']).dt.month_name()
            # Group by month
            monthly_data = analysis_data.groupby('Month')['Total_Cyclists'].mean().reset_index()
            # Add weather data averages
            monthly_weather = analysis_data.groupby('Month').agg({
                'temp_max': 'mean',
                'precipitation': 'mean'
            }).reset_index()
            monthly_data = pd.merge(monthly_data, monthly_weather, on='Month')
            
            # Sort by month order
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                         'July', 'August', 'September', 'October', 'November', 'December']
            monthly_data['Month'] = pd.Categorical(monthly_data['Month'], categories=month_order, ordered=True)
            monthly_data = monthly_data.sort_values('Month')
            
            # Create dual-axis chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_data['Month'],
                y=monthly_data['Total_Cyclists'],
                name='Average Daily Cyclists',
                marker_color='steelblue'
            ))
            fig.add_trace(go.Scatter(
                x=monthly_data['Month'],
                y=monthly_data['temp_max'],
                name='Avg Max Temperature (°C)',
                marker_color='orangered',
                yaxis='y2'
            ))
            
            # Set up the layout with dual y-axes
            fig.update_layout(
                title='Monthly Bicycle Usage and Temperature Trends',
                xaxis=dict(title='Month'),
                yaxis=dict(title='Average Daily Cyclists', side='left'),
                yaxis2=dict(title='Avg Max Temperature (°C)', overlaying='y', side='right'),
                legend=dict(x=0.01, y=0.99, orientation='h')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. Day of week patterns
            st.subheader("Daily and Hourly Patterns")
            
            # Add day of week
            filtered_data['DayOfWeek'] = pd.to_datetime(filtered_data['Time']).dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            filtered_data['DayOfWeek'] = pd.Categorical(filtered_data['DayOfWeek'], categories=day_order, ordered=True)
            
            # Group by day of week and hour
            hourly_patterns = filtered_data.groupby(['DayOfWeek', 'Hour'])['Count'].mean().reset_index()
            
            # Create heatmap of hourly patterns by day of week
            pivot_data = hourly_patterns.pivot(index='Hour', columns='DayOfWeek', values='Count')
            
            fig = px.imshow(pivot_data, 
                          labels=dict(x="Day of Week", y="Hour of Day", color="Average Cyclists"),
                          x=day_order,
                          y=list(range(24)),
                          color_continuous_scale='Viridis',
                          title='Bicycle Usage Patterns by Hour and Day of Week')
            
            fig.update_layout(coloraxis_colorbar=dict(title='Avg. Cyclists'))
            st.plotly_chart(fig, use_container_width=True)
            
            # 5. Atmospheric pressure effect on cycling
            st.subheader("Impact of Atmospheric Pressure on Cycling")
            
            fig = px.scatter(analysis_data, x='pressure', y='Total_Cyclists',
                           title='How Atmospheric Pressure Affects Cycling in Dublin',
                           color='temp_max', hover_data=['date'])
            fig.update_layout(xaxis_title='Atmospheric Pressure (hPa)',
                            yaxis_title='Total Daily Cyclists',
                            coloraxis_colorbar_title='Max Temp (°C)')
            st.plotly_chart(fig, use_container_width=True)
            
            # 6. Seasonal comparison
            st.subheader("Seasonal Bicycle Usage Comparison")
            
            # Add season to analysis data
            analysis_data['Month_Num'] = pd.to_datetime(analysis_data['date']).dt.month
            analysis_data['Season'] = analysis_data['Month_Num'].apply(lambda x: 
                'Winter' if x in [12, 1, 2] else
                'Spring' if x in [3, 4, 5] else
                'Summer' if x in [6, 7, 8] else
                'Autumn')
            
            # Group by season
            seasonal_data = analysis_data.groupby('Season')['Total_Cyclists'].mean().reset_index()
            
            # Order seasons
            season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
            seasonal_data['Season'] = pd.Categorical(seasonal_data['Season'], categories=season_order, ordered=True)
            seasonal_data = seasonal_data.sort_values('Season')
            
            fig = px.bar(seasonal_data, x='Season', y='Total_Cyclists',
                       title='Average Daily Cyclists by Season',
                       color='Season', 
                       color_discrete_map={'Winter': 'skyblue', 'Spring': 'yellowgreen', 
                                           'Summer': 'orange', 'Autumn': 'brown'})
            fig.update_layout(xaxis_title='Season',
                            yaxis_title='Average Daily Cyclists')
            st.plotly_chart(fig, use_container_width=True)
            
            # Replace the year-over-year trends with a simple year comparison 
            st.subheader("Yearly Comparison")
            
            # Group by year for a simple comparison
            analysis_data['Year'] = pd.to_datetime(analysis_data['date']).dt.year
            yearly_data = analysis_data.groupby('Year')['Total_Cyclists'].mean().reset_index()
            
            # Display yearly comparison bar chart
            fig = px.bar(yearly_data, x='Year', y='Total_Cyclists',
                      title='Average Daily Cyclists by Year',
                      color='Year')
            fig.update_layout(xaxis_title='Year',
                           yaxis_title='Average Daily Cyclists')
            st.plotly_chart(fig, use_container_width=True)
            
            # 8. Temperature range effect
            st.subheader("Temperature Range Effect")
            
            # Calculate temperature range
            analysis_data['temp_range'] = analysis_data['temp_max'] - analysis_data['temp_min']
            
            fig = px.scatter(analysis_data, x='temp_range', y='Total_Cyclists',
                           title='Impact of Daily Temperature Range on Cycling',
                           color='temp_max', hover_data=['date'])
            fig.update_layout(xaxis_title='Temperature Range (°C)',
                            yaxis_title='Total Daily Cyclists',
                            coloraxis_colorbar_title='Max Temp (°C)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Show hourly and location-based patterns even without full analysis
    st.header("Basic Bicycle Usage Patterns")
    
    # Hourly patterns
    st.subheader("Hourly Bicycle Usage Patterns")
    hourly_data = filtered_data.groupby('Hour')['Count'].mean().reset_index()
    
    fig = px.line(hourly_data, x='Hour', y='Count',
                title='Average Hourly Bicycle Usage',
                markers=True)
    fig.update_layout(xaxis_title='Hour of Day (24h)',
                    yaxis_title='Average Cyclists')
    st.plotly_chart(fig, use_container_width=True)
    
    # Location comparison
    st.subheader("Bicycle Usage by Location")
    location_data = filtered_data.groupby('Location')['Count'].sum().reset_index()
    location_data = location_data.sort_values('Count', ascending=False)
    
    fig = px.bar(location_data, x='Location', y='Count',
               title='Total Bicycle Counts by Location')
    fig.update_layout(xaxis_title='Location',
                    yaxis_title='Total Cyclists',
                    xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly patterns
    st.subheader("Monthly Bicycle Usage Patterns")
    monthly_data = filtered_data.groupby('Month')['Count'].mean().reset_index()
    # Order months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_data['Month'] = pd.Categorical(monthly_data['Month'], categories=month_order, ordered=True)
    monthly_data = monthly_data.sort_values('Month')
    
    fig = px.line(monthly_data, x='Month', y='Count',
                title='Average Monthly Bicycle Usage',
                markers=True)
    fig.update_layout(xaxis_title='Month',
                    yaxis_title='Average Cyclists')
    st.plotly_chart(fig, use_container_width=True)
    
    # Add information about how to use the analysis
    st.info("""
    **How to use this analysis:**
    
    1. Use the filters at the top to select specific years (2020-2022), locations, seasons, and time periods.
    2. Click the "Analyze Weather Correlation" button to see detailed weather impact visualizations.
    3. Explore the patterns to understand how weather affects cycling habits in Dublin.
    
    The visualizations show relationships between bicycle usage and various weather parameters like temperature, precipitation, and atmospheric pressure using actual Dublin weather data from 2020-2022.
    """)
