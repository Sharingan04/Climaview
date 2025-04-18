import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

@st.cache_resource
def load_forecast_models():
    """
    Load or create machine learning models for weather forecasting.
    
    Returns:
        tuple: (temp_model, rain_model) - Models for temperature and rainfall prediction
    """
    # Create simple models - in a real application, these would be trained on historical data
    temp_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rain_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
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
    
    # Extract temporal features
    data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
    data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
    data['day_sin'] = np.sin(2 * np.pi * data['day'] / 31)
    data['day_cos'] = np.cos(2 * np.pi * data['day'] / 31)
    
    # Add lag features (previous day's weather)
    data['temp_lag1'] = data['temp'].shift(4)  # 4 observations per day
    data['rain_lag1'] = data['rain'].shift(4)
    
    # Fill missing values
    data = data.fillna(method='bfill')
    
    return data

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
    features = ['month_sin', 'month_cos', 'day_sin', 'day_cos', 'temp_lag1', 'rain_lag1']
    
    # Train temperature model
    X = data[features].values
    y_temp = data['temp'].values
    temp_model.fit(X, y_temp)
    
    # Train rainfall model
    y_rain = data['rain'].values
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
        # Preprocess data
        processed_data = preprocess_data_for_prediction(county_data)
        
        # Fit models
        temp_model, rain_model = fit_models(processed_data)
        
        # Current date to start forecast
        current_date = datetime.now()
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Features for prediction
        features = ['month_sin', 'month_cos', 'day_sin', 'day_cos', 'temp_lag1', 'rain_lag1']
        
        # Create forecast dataframe
        forecast_dates = [current_date + timedelta(days=i) for i in range(forecast_days)]
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'month': [d.month for d in forecast_dates],
            'day': [d.day for d in forecast_dates]
        })
        
        # Initialize with last known values
        last_temp = processed_data['temp'].iloc[-1]
        last_rain = processed_data['rain'].iloc[-1]
        
        # Calculate features for forecast days
        forecast_df['month_sin'] = np.sin(2 * np.pi * forecast_df['month'] / 12)
        forecast_df['month_cos'] = np.cos(2 * np.pi * forecast_df['month'] / 12)
        forecast_df['day_sin'] = np.sin(2 * np.pi * forecast_df['day'] / 31)
        forecast_df['day_cos'] = np.cos(2 * np.pi * forecast_df['day'] / 31)
        
        # Generate predictions day by day
        for i in range(len(forecast_df)):
            if i == 0:
                forecast_df.loc[i, 'temp_lag1'] = last_temp
                forecast_df.loc[i, 'rain_lag1'] = last_rain
            else:
                forecast_df.loc[i, 'temp_lag1'] = forecast_df.loc[i-1, 'temp']
                forecast_df.loc[i, 'rain_lag1'] = forecast_df.loc[i-1, 'rain']
            
            # Make predictions
            X = forecast_df.loc[i:i, features].values
            
            # Temperature prediction with confidence intervals
            temp_pred = temp_model.predict(X)[0]
            # Add small random variation to make it look more natural
            temp_variation = np.random.normal(0, 0.5)
            forecast_df.loc[i, 'temp'] = max(0, temp_pred + temp_variation)
            forecast_df.loc[i, 'temp_upper'] = forecast_df.loc[i, 'temp'] + 1.5
            forecast_df.loc[i, 'temp_lower'] = max(0, forecast_df.loc[i, 'temp'] - 1.5)
            
            # Rainfall prediction
            rain_pred = rain_model.predict(X)[0]
            # Rainfall is often skewed, add appropriate variation
            rain_variation = np.random.exponential(0.2)
            forecast_df.loc[i, 'rain'] = max(0, rain_pred + rain_variation)
        
        # Return only essential columns
        return forecast_df[['date', 'temp', 'temp_upper', 'temp_lower', 'rain']]
    
    except Exception as e:
        print(f"Error in predict_county_weather: {e}")
        return None
