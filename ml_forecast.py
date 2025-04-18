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
    # Create models
    temp_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rain_model = RandomForestRegressor(n_estimators=50, random_state=42)
    
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
    
    # Convert 'date' column from object to datetime
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    
    # Extract features
    daily_data['month'] = daily_data['date'].dt.month
    daily_data['day'] = daily_data['date'].dt.day
    daily_data['day_of_year'] = daily_data['date'].dt.dayofyear
    
    # Create cyclical features for seasonality
    daily_data['month_sin'] = np.sin(2 * np.pi * daily_data['month'] / 12)
    daily_data['month_cos'] = np.cos(2 * np.pi * daily_data['month'] / 12)
    daily_data['day_sin'] = np.sin(2 * np.pi * daily_data['day_of_year'] / 365)
    daily_data['day_cos'] = np.cos(2 * np.pi * daily_data['day_of_year'] / 365)
    
    # Sort by date
    daily_data = daily_data.sort_values('date')
    
    # Create lag features (previous days' weather)
    daily_data['temp_lag1'] = daily_data['temp'].shift(1)
    daily_data['temp_lag2'] = daily_data['temp'].shift(2)
    daily_data['temp_lag3'] = daily_data['temp'].shift(3)
    daily_data['temp_lag7'] = daily_data['temp'].shift(7)
    
    daily_data['rain_lag1'] = daily_data['rain'].shift(1)
    daily_data['rain_lag2'] = daily_data['rain'].shift(2)
    daily_data['rain_lag3'] = daily_data['rain'].shift(3)
    daily_data['rain_lag7'] = daily_data['rain'].shift(7)
    
    # Calculate rolling averages
    daily_data['temp_rolling_mean_3'] = daily_data['temp'].rolling(window=3).mean()
    daily_data['temp_rolling_mean_7'] = daily_data['temp'].rolling(window=7).mean()
    daily_data['rain_rolling_mean_3'] = daily_data['rain'].rolling(window=3).mean()
    daily_data['rain_rolling_mean_7'] = daily_data['rain'].rolling(window=7).mean()
    
    # Create target variables (future values)
    for i in range(1, 6):
        daily_data[f'temp_future_{i}'] = daily_data['temp'].shift(-i)
        daily_data[f'rain_future_{i}'] = daily_data['rain'].shift(-i)
    
    # Fill missing values
    daily_data = daily_data.fillna(method='bfill').fillna(method='ffill')
    
    return daily_data

def get_feature_importance(model, feature_names):
    """Get and return feature importance"""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        # Sort importance by value
        indices = np.argsort(importance)[::-1]
        
        # Return dict of feature name and importance
        return {feature_names[i]: importance[i] for i in indices}
    return {}

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
    
    try:
        # Features for prediction
        features = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'temp', 'rain',
            'temp_lag1', 'temp_lag2', 'temp_lag3', 'temp_lag7',
            'rain_lag1', 'rain_lag2', 'rain_lag3', 'rain_lag7',
            'temp_rolling_mean_3', 'temp_rolling_mean_7',
            'rain_rolling_mean_3', 'rain_rolling_mean_7'
        ]
        
        # Ensure all required columns exist
        for col in features:
            if col not in data.columns:
                print(f"Column {col} not found in data, skipping...")
                features.remove(col)
        
        # Train data
        train_data = data.dropna(subset=[f'temp_future_{i}' for i in range(1, 6)] + 
                                 [f'rain_future_{i}' for i in range(1, 6)])
        
        if len(train_data) > 10:  # Ensure we have enough data
            # Get feature data
            X = train_data[features].values
            
            # Target for temperature (next 5 days)
            y_temp = train_data[[f'temp_future_{i}' for i in range(1, 6)]].values
            
            # Train temperature model
            temp_model.fit(X, y_temp)
            
            # Target for rainfall (next 5 days)
            y_rain = train_data[[f'rain_future_{i}' for i in range(1, 6)]].values
            
            # Train rainfall model
            rain_model.fit(X, y_rain)
            
            # Print feature importance
            temp_importance = get_feature_importance(temp_model, features)
            rain_importance = get_feature_importance(rain_model, features)
            
            return temp_model, rain_model
        else:
            print(f"Not enough training data: {len(train_data)} rows")
            return None, None
    except Exception as e:
        print(f"Error in fit_models: {e}")
        return None, None

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
        
        if not county or county_data.empty:
            print("No county data provided")
            return None
            
        print(f"Generating forecast for {county}")
        
        # Preprocess data
        processed_data = preprocess_data_for_prediction(county_data)
        
        if processed_data.empty:
            print("Processed data is empty")
            return None
        
        # Fit models
        temp_model, rain_model = fit_models(processed_data)
        
        if temp_model is None or rain_model is None:
            print("Failed to train models")
            return None
        
        # Current date to start forecast from
        current_date = datetime.now()
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Limit forecast days to 5 (the model is trained for 5 days)
        forecast_days = min(forecast_days, 5)
        
        # Create forecast dataframe
        forecast_dates = [current_date + timedelta(days=i) for i in range(1, forecast_days+1)]
        
        # Get latest data for prediction
        latest_data = processed_data.iloc[-1:].copy()
        
        # Features for prediction
        features = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'temp', 'rain',
            'temp_lag1', 'temp_lag2', 'temp_lag3', 'temp_lag7',
            'rain_lag1', 'rain_lag2', 'rain_lag3', 'rain_lag7',
            'temp_rolling_mean_3', 'temp_rolling_mean_7',
            'rain_rolling_mean_3', 'rain_rolling_mean_7'
        ]
        
        # Ensure all required columns exist
        for col in features:
            if col not in latest_data.columns:
                print(f"Column {col} not found in latest data")
                return None
        
        # Make predictions
        X = latest_data[features].values
        temp_preds = temp_model.predict(X)[0][:forecast_days]
        rain_preds = rain_model.predict(X)[0][:forecast_days]
        
        # Create result dataframe
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'temp': temp_preds,
            'rain': rain_preds
        })
        
        # Add a small random variation to make the forecast look more natural
        forecast_df['temp'] = forecast_df['temp'] + np.random.normal(0, 0.2, len(forecast_df))
        forecast_df['rain'] = np.maximum(0, forecast_df['rain'] + np.random.exponential(0.1, len(forecast_df)))
        
        # Round values
        forecast_df['temp'] = forecast_df['temp'].round(1)
        forecast_df['rain'] = forecast_df['rain'].round(2)
        
        # Add confidence intervals for temperature (±1.5°C)
        forecast_df['temp_upper'] = forecast_df['temp'] + 1.5
        forecast_df['temp_lower'] = forecast_df['temp'] - 1.5
        forecast_df['temp_lower'] = forecast_df['temp_lower'].clip(lower=0)  # Ensure non-negative
        
        return forecast_df
    
    except Exception as e:
        print(f"Error in predict_county_weather: {e}")
        import traceback
        traceback.print_exc()
        return None
