import requests
import json
import os
import pandas as pd
from datetime import datetime
import sys

# Constants
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "London"
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

def fetch_weather_data():
    if not API_KEY:
        print("Error: OPENWEATHER_API_KEY not found in environment variables.")
        sys.exit(1)

    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant fields
        records = []
        for item in data['list']:
            record = {
                "dt": item['dt'],
                "dt_txt": item['dt_txt'],
                "temp": item['main']['temp'],
                "feels_like": item['main']['feels_like'],
                "pressure": item['main']['pressure'],
                "humidity": item['main']['humidity'],
                "weather_main": item['weather'][0]['main'],
                "weather_description": item['weather'][0]['description'],
                "wind_speed": item['wind']['speed'],
                "wind_deg": item['wind']['deg'],
                "clouds_all": item['clouds']['all'],
                "collection_time": datetime.now().isoformat()
            }
            records.append(record)
            
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Save to raw data folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "/opt/airflow/dags/data/raw" # Path inside Docker container
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/weather_raw_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully saved data to {filename}")
        return filename

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_weather_data()
