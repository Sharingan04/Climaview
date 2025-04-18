import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
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

def plot_temperature_by_county(df, selected_counties, year, month=None):
    """Create a line plot of temperature data for selected counties.
    
    Args:
        df (pandas.DataFrame): Weather data
        selected_counties (list): List of county names to display
        year (int): Year to filter data
        month (int, optional): Month to filter data
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure with temperature plot
    """
    # Filter the dataframe by selected counties and year
    filtered_df = df[df['county'].isin(selected_counties) & (df['year'] == year)]
    
    # Filter by month if provided
    if month:
        filtered_df = filtered_df[filtered_df['month'] == month]
    
    # Group by county and date, calculate average temperature
    grouped_df = filtered_df.groupby(['county', pd.Grouper(key='date', freq='D')])['temp'].mean().reset_index()
    
    # Create the line plot
    fig = px.line(
        grouped_df,
        x='date',
        y='temp',
        color='county',
        title='Average Daily Temperature by County',
        labels={'temp': 'Temperature (°C)', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=500,
        legend_title='County',
        hovermode='x unified'
    )
    
    return fig

def plot_rainfall_by_county(df, selected_counties, year, month=None):
    """Create a bar plot of rainfall data for selected counties.
    
    Args:
        df (pandas.DataFrame): Weather data
        selected_counties (list): List of county names to display
        year (int): Year to filter data
        month (int, optional): Month to filter data
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure with rainfall plot
    """
    # Filter the dataframe by selected counties and year
    filtered_df = df[df['county'].isin(selected_counties) & (df['year'] == year)]
    
    # Filter by month if provided
    if month:
        filtered_df = filtered_df[filtered_df['month'] == month]
    
    # Group by county and date, sum rainfall
    grouped_df = filtered_df.groupby(['county', pd.Grouper(key='date', freq='D')])['rain'].sum().reset_index()
    
    # Create the bar plot
    fig = px.bar(
        grouped_df,
        x='date',
        y='rain',
        color='county',
        title='Daily Rainfall by County',
        labels={'rain': 'Rainfall (mm)', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=500,
        legend_title='County',
        hovermode='x unified',
        barmode='group'
    )
    
    return fig

def create_temperature_heatmap(df, selected_county, year):
    """Create a heatmap of temperature data for a selected county.
    
    Args:
        df (pandas.DataFrame): Weather data
        selected_county (str): County name to display
        year (int): Year to filter data
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure with temperature heatmap
    """
    # Filter the dataframe by selected county and year
    filtered_df = df[(df['county'] == selected_county) & (df['year'] == year)]
    
    # Group by month and day, calculate average temperature
    pivot_df = filtered_df.groupby(['month', 'day'])['temp'].mean().reset_index()
    
    # Create a pivot table with months as rows and days as columns
    pivot_table = pivot_df.pivot(index='month', columns='day', values='temp')
    
    # Create the heatmap
    fig = px.imshow(
        pivot_table,
        labels=dict(x='Day of Month', y='Month', color='Temperature (°C)'),
        x=pivot_table.columns,
        y=pivot_table.index,
        title=f'Temperature Heatmap for {selected_county} in {year}',
        color_continuous_scale='RdBu_r'
    )
    
    fig.update_layout(
        height=500,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 32, 5)),
            ticktext=[str(day) for day in range(1, 32, 5)]
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        )
    )
    
    return fig

def create_county_comparison_chart(df, selected_counties, year, metric='temp'):
    """Create a box plot comparing weather metrics across counties.
    
    Args:
        df (pandas.DataFrame): Weather data
        selected_counties (list): List of county names to display
        year (int): Year to filter data
        metric (str): Weather metric to compare ('temp' or 'rain')
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure with comparison chart
    """
    # Filter the dataframe by selected counties and year
    filtered_df = df[df['county'].isin(selected_counties) & (df['year'] == year)]
    
    # Create the box plot
    metric_title = 'Temperature (°C)' if metric == 'temp' else 'Rainfall (mm)'
    
    fig = px.box(
        filtered_df,
        x='county',
        y=metric,
        color='county',
        title=f'Comparison of {metric_title} Across Counties in {year}',
        labels={metric: metric_title, 'county': 'County'}
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_title=None
    )
    
    return fig
