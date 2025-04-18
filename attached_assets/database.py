import sqlite3
import pandas as pd
from datetime import datetime

def initialize_db():
    """Initialize SQLite database with tables for weather data."""
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    
    # Create table for weather data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        country TEXT,
        timestamp DATETIME NOT NULL,
        temperature REAL,
        feels_like REAL,
        temp_min REAL,
        temp_max REAL,
        pressure INTEGER,
        humidity INTEGER,
        wind_speed REAL,
        wind_deg INTEGER,
        clouds INTEGER,
        weather_main TEXT,
        weather_description TEXT,
        latitude REAL,
        longitude REAL
    )
    ''')
    
    conn.commit()
    conn.close()

def store_weather_data(weather_data):
    """Store weather data in the database.
    
    Args:
        weather_data (dict): Formatted weather data to store
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    
    # Check if we already have a recent entry for this city (within last hour)
    cursor.execute('''
    SELECT * FROM weather_data 
    WHERE city = ? AND timestamp > datetime('now', '-1 hour')
    ''', (weather_data['city'],))
    
    existing_data = cursor.fetchone()
    
    # Only insert if we don't have recent data
    if not existing_data:
        cursor.execute('''
        INSERT INTO weather_data (
            city, country, timestamp, temperature, feels_like, 
            temp_min, temp_max, pressure, humidity, wind_speed, 
            wind_deg, clouds, weather_main, weather_description,
            latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            weather_data['city'],
            weather_data['country'],
            weather_data['timestamp'],
            weather_data['temperature'],
            weather_data['feels_like'],
            weather_data['temp_min'],
            weather_data['temp_max'],
            weather_data['pressure'],
            weather_data['humidity'],
            weather_data['wind_speed'],
            weather_data['wind_deg'],
            weather_data['clouds'],
            weather_data['weather_main'],
            weather_data['weather_description'],
            weather_data['latitude'],
            weather_data['longitude']
        ))
        
        conn.commit()
    
    conn.close()

def get_historical_data(city, start_date, end_date):
    """Get historical weather data for a city within a date range.
    
    Args:
        city (str): City name
        start_date (datetime): Start date for data retrieval
        end_date (datetime): End date for data retrieval
        
    Returns:
        pandas.DataFrame: Historical weather data
    """
    conn = sqlite3.connect('weather_data.db')
    
    query = '''
    SELECT * FROM weather_data 
    WHERE city = ? AND timestamp BETWEEN ? AND ?
    ORDER BY timestamp ASC
    '''
    
    # Format dates to strings for SQLite
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    df = pd.read_sql_query(
        query, 
        conn, 
        params=(city, start_date_str, end_date_str)
    )
    
    conn.close()
    
    # Convert timestamp string to datetime object
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def get_cities_with_data():
    """Get a list of cities for which we have weather data.
    
    Returns:
        list: List of city names
    """
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT DISTINCT city FROM weather_data
    ORDER BY city ASC
    ''')
    
    cities = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return cities
