import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

# County-specific forecast data based on the notebook
IRELAND_FORECAST_DATA = {
    'Carlow': {'temp': [10.64, 10.64, 10.63, 10.59, 10.59], 'rain': [1.91, 1.98, 2.04, 2.03, 2.11]},
    'Cavan': {'temp': [8.89, 8.98, 9.01, 9.01, 9.02], 'rain': [2.39, 2.57, 2.61, 2.59, 2.66]},
    'Clare': {'temp': [9.18, 9.34, 9.41, 9.41, 9.44], 'rain': [2.32, 2.56, 2.63, 2.69, 2.74]},
    'Cork': {'temp': [11.87, 11.85, 11.79, 11.72, 11.74], 'rain': [6.87, 7.49, 7.59, 7.88, 8.27]},
    'Donegal': {'temp': [8.18, 8.33, 8.41, 8.48, 8.5], 'rain': [2.96, 3.11, 3.16, 3.15, 3.03]},
    'Dublin': {'temp': [9.26, 9.37, 9.39, 9.39, 9.4], 'rain': [3.59, 3.67, 3.7, 3.92, 4.01]},
    'Galway': {'temp': [8.86, 9.02, 9.11, 9.15, 9.21], 'rain': [2.72, 2.83, 2.87, 2.89, 2.96]},
    'Mayo': {'temp': [7.47, 7.73, 7.86, 7.96, 8.04], 'rain': [5.07, 5.21, 5.2, 5.26, 5.19]},
    'Meath': {'temp': [9.66, 9.7, 9.68, 9.65, 9.67], 'rain': [1.97, 2.13, 2.09, 2.26, 2.3]},
    'Roscommon': {'temp': [8.66, 8.77, 8.82, 8.84, 8.87], 'rain': [2.66, 2.92, 2.9, 2.94, 2.89]},
    'Sligo': {'temp': [7.26, 7.5, 7.61, 7.71, 7.77], 'rain': [3.75, 3.73, 3.73, 3.74, 3.72]},
    'Tipperary': {'temp': [12.12, 11.94, 11.82, 11.69, 11.64], 'rain': [1.95, 2.11, 2.2, 2.24, 2.28]},
    'Westmeath': {'temp': [9.12, 9.2, 9.23, 9.22, 9.23], 'rain': [2.19, 2.38, 2.42, 2.55, 2.53]},
    'Wexford': {'temp': [10.55, 10.58, 10.57, 10.54, 10.56], 'rain': [2.36, 2.55, 2.63, 2.67, 2.68]}
}

@st.cache_resource
def load_forecast_models():
    """
    Load or create machine learning models for weather forecasting.
    
    Returns:
        tuple: (temp_model, rain_model) - Models for temperature and rainfall prediction
    """
    # Create simple models - in a real application, these would be trained on historical data
    temp_model = LinearRegression()
    rain_model = LinearRegression()
    
    return temp_model, rain_model

def preprocess_data_for_prediction(county_data):
    """
    Preprocess county weather data for prediction.
    
    Args:
        county_data (pandas.DataFrame): Historical weather data for a county
        
    Returns:
        pandas.DataFrame: Processed data with features for prediction
    """
    # Create a copy to avoid modifying the original data
    data = county_data.copy()
    
    # Group by day to get daily values
    daily_data = data.groupby([data['date'].dt.date, 'county']).agg({
        'temp': 'mean',
        'rain': 'sum'
    }).reset_index()
    
    # Extract temporal features
    daily_data['month'] = pd.to_datetime(daily_data['date']).dt.month
    daily_data['day'] = pd.to_datetime(daily_data['date']).dt.day
    
    return daily_data

def fit_models(data):
    """
    Fit prediction models on historical data.
    
    Args:
        data (pandas.DataFrame): Processed historical weather data
        
    Returns:
        tuple: (temp_model, rain_model) - Fitted models
    """
    # Load models
    temp_model, rain_model = load_forecast_models()
    
    # Features for prediction
    features = ['temp', 'rain']
    
    # Create target variables (t+1 to t+5)
    for i in range(1, 6):
        data[f'temp_t+{i}'] = data.groupby('county')['temp'].shift(-i)
        data[f'rain_t+{i}'] = data.groupby('county')['rain'].shift(-i)
    
    # Drop NaN values
    train_data = data.dropna()
    
    if len(train_data) > 0:
        # Train temperature model
        X = train_data[features].values
        y_temp = train_data[[f'temp_t+{i}' for i in range(1, 6)]].values
        temp_model.fit(X, y_temp)
        
        # Train rainfall model
        y_rain = train_data[[f'rain_t+{i}' for i in range(1, 6)]].values
        rain_model.fit(X, y_rain)
    
    return temp_model, rain_model

def predict_county_weather(county_data, forecast_days=7):
    """
    Generate weather forecast for a county.
    
    Args:
        county_data (pandas.DataFrame): Historical weather data for a county
        forecast_days (int): Number of days to forecast
        
    Returns:
        pandas.DataFrame: Forecast data with temperature and rainfall predictions
    """
    try:
        # Get county name
        county = county_data['county'].iloc[0] if not county_data.empty else None
        
        if county and county in IRELAND_FORECAST_DATA:
            # Use pre-calculated forecast data
            forecast_data = IRELAND_FORECAST_DATA[county]
            
            # Limit to requested days
            days = min(forecast_days, 5)  # We have 5 days of data
            
            # Create dataframe
            current_date = datetime.now()
            current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            forecast_dates = [current_date + timedelta(days=i) for i in range(1, days+1)]
            
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'temp': forecast_data['temp'][:days],
                'rain': forecast_data['rain'][:days]
            })
            
            # Add confidence intervals for temperature
            forecast_df['temp_upper'] = forecast_df['temp'] + 1.5
            forecast_df['temp_lower'] = forecast_df['temp'] - 1.5
            forecast_df['temp_lower'] = forecast_df['temp_lower'].clip(lower=0)  # Ensure non-negative
            
            return forecast_df
        
        # Fall back to model-based prediction if county not in forecast data
        # Preprocess data
        processed_data = preprocess_data_for_prediction(county_data)
        
        if processed_data.empty:
            return None
        
        # Fit models
        temp_model, rain_model = fit_models(processed_data)
        
        # Current date to start forecast
        current_date = datetime.now()
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create forecast dataframe
        forecast_dates = [current_date + timedelta(days=i) for i in range(1, forecast_days+1)]
        
        # Get the latest temperature and rainfall data
        latest_data = processed_data.iloc[-1]
        features = [latest_data['temp'], latest_data['rain']]
        
        # Make predictions
        X = np.array([features])
        temp_preds = temp_model.predict(X)[0][:forecast_days]
        rain_preds = rain_model.predict(X)[0][:forecast_days]
        
        # Create result dataframe
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'temp': temp_preds,
            'rain': rain_preds
        })
        
        # Add confidence intervals for temperature
        forecast_df['temp_upper'] = forecast_df['temp'] + 1.5
        forecast_df['temp_lower'] = forecast_df['temp'] - 1.5
        forecast_df['temp_lower'] = forecast_df['temp_lower'].clip(lower=0)  # Ensure non-negative
        
        return forecast_df
    
    except Exception as e:
        print(f"Error in predict_county_weather: {e}")
        return None
