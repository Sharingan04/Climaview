import pandas as pd

def load_bicycle_data():
    """
    Load and process bicycle data from the CSV files for 2020-2022 only
    """
    print("Loading bicycle data for years 2020-2022 only...")
    # Initialize dataframes for years 2020-2022
    df_2020 = pd.read_csv('attached_assets/jan-dec-2020-cycle-data.csv')
    df_2021 = pd.read_csv('attached_assets/2021-dublin-city-cycle-counts-31122021.csv')
    df_2022 = pd.read_csv('attached_assets/cycle-counts-2022.csv')
    
    # Process 2020 data
    df_2020['Time'] = pd.to_datetime(df_2020['Time'], format='%d-%m-%Y %H:%M:%S')
    # For 2020, handle IN and OUT columns differently
    location_cols = [col for col in df_2020.columns if 'IN' not in col and 'OUT' not in col and col != 'Time']
    df_2020_processed = df_2020.melt(
        id_vars=['Time'],
        value_vars=location_cols,
        var_name='Location',
        value_name='Count'
    )
    df_2020_processed['Year'] = df_2020_processed['Time'].dt.year
    
    # Process 2021 data
    df_2021['Time'] = pd.to_datetime(df_2021['Time'], format='%d-%m-%Y %H:%M:%S')
    # Filter for total counts (not IN/OUT directions)
    location_cols = [col for col in df_2021.columns if 'Cyclist IN' not in col and 'Cyclist OUT' not in col and 'Time' not in col]
    location_cols = [col for col in location_cols if not any(substr in col for substr in ['IN', 'OUT'])]
    df_2021_processed = df_2021.melt(
        id_vars=['Time'],
        value_vars=location_cols,
        var_name='Location',
        value_name='Count'
    )
    df_2021_processed['Year'] = df_2021_processed['Time'].dt.year
    
    # Process 2022 data
    df_2022['Time'] = pd.to_datetime(df_2022['Time'], format='%d/%m/%Y %H:%M')
    # Filter for total counts (not IN/OUT directions)
    location_cols = [col for col in df_2022.columns if 'Cyclist IN' not in col and 'Cyclist OUT' not in col and 'Time' not in col]
    location_cols = [col for col in location_cols if not any(substr in col for substr in ['IN', 'OUT'])]
    df_2022_processed = df_2022.melt(
        id_vars=['Time'],
        value_vars=location_cols,
        var_name='Location',
        value_name='Count'
    )
    df_2022_processed['Year'] = df_2022_processed['Time'].dt.year
    
    # Combine the processed dataframes for 2020-2022
    combined_df = pd.concat([df_2020_processed, df_2021_processed, df_2022_processed], ignore_index=True)
    
    # Add date components for easier analysis
    combined_df['Date'] = combined_df['Time'].dt.date
    combined_df['Hour'] = combined_df['Time'].dt.hour
    combined_df['Day'] = combined_df['Time'].dt.day_name()
    combined_df['Month'] = combined_df['Time'].dt.month_name()
    combined_df['Season'] = combined_df['Time'].dt.month.apply(get_season)
    
    print(f"Loaded {len(combined_df)} bicycle records from 2020-2022")
    return combined_df

def get_season(month):
    """Determine season based on month number"""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

def get_weather_data(city="Dublin", start_date=None, end_date=None):
    """
    Load actual Dublin weather data from the CSV file
    and filter for the requested date range.
    """
    # Load the actual Dublin weather data
    print("Loading actual Dublin weather data from CSV file...")
    try:
        weather_df = pd.read_csv('attached_assets/counties_with_data_2015_2022.csv')
        
        # Filter for Dublin data only
        weather_df = weather_df[weather_df['county'] == 'Dublin']
        
        # Convert date to datetime
        weather_df['date'] = pd.to_datetime(weather_df['date'], format='%d-%m-%Y %H:%M')
        
        # Add a year column for debugging
        weather_df['year'] = weather_df['date'].dt.year
        
        # Check years in source data
        years_in_source = sorted(list(weather_df['year'].unique()))
        print(f"Years in weather source data: {years_in_source}")
        
        # Make sure we keep data from 2020-2022 (with some tolerance in case the date formats are off)
        weather_df = weather_df[(weather_df['year'] >= 2020) & (weather_df['year'] <= 2022)]
        
        # Create daily aggregations 
        daily_weather = weather_df.groupby(weather_df['date'].dt.date).agg({
            'temp': ['max', 'min', 'mean'],
            'rain': 'sum',
            'rhum': 'mean', 
            'msl': 'mean',  # Atmospheric pressure
            'year': 'first'  # Keep the year for debugging
        }).reset_index()
        
        # Flatten multi-level columns
        daily_weather.columns = ['date', 'temp_max', 'temp_min', 'temp_mean', 'precipitation', 'humidity', 'pressure', 'year']
        
        # Check years in daily aggregation
        years_in_daily = sorted(list(daily_weather['year'].unique()))
        print(f"Years in daily weather data: {years_in_daily}")
        
        # Print count of records per year for debugging
        year_counts = daily_weather['year'].value_counts().sort_index()
        print(f"Daily weather records per year: {year_counts.to_dict()}")
        
        # Filter by date range if specified
        if start_date is not None:
            daily_weather = daily_weather[daily_weather['date'] >= start_date]
        if end_date is not None:
            daily_weather = daily_weather[daily_weather['date'] <= end_date]
            
        print(f"Loaded {len(daily_weather)} days of actual Dublin weather data")
        return daily_weather
        
    except Exception as e:
        print(f"Error loading weather data: {e}")
        # Return empty DataFrame if file can't be loaded
        return pd.DataFrame(columns=['date', 'temp_max', 'temp_min', 'temp_mean', 
                                    'precipitation', 'humidity', 'pressure', 'year'])

def preprocess_data_for_analysis(bicycle_df, weather_df):
    """
    Preprocess and merge bicycle and weather data for analysis
    """
    # Aggregate bicycle data by date
    daily_bicycle_data = bicycle_df.groupby('Date')['Count'].sum().reset_index()
    daily_bicycle_data.rename(columns={'Count': 'Total_Cyclists'}, inplace=True)
    
    # Merge with weather data
    weather_df['date'] = pd.to_datetime(weather_df['date']).dt.date
    merged_data = pd.merge(daily_bicycle_data, weather_df, left_on='Date', right_on='date', how='inner')
    
    return merged_data
