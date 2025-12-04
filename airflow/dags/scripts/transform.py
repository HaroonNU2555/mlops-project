import pandas as pd
import sys
import os
import glob
from datetime import datetime
import mlflow
from ydata_profiling import ProfileReport

# Constants
RAW_DATA_DIR = "/opt/airflow/dags/data/raw"
PROCESSED_DATA_DIR = "/opt/airflow/dags/data/processed"
MLFLOW_TRACKING_URI = "http://mlflow:5000"

def transform_data():
    # Find latest file
    list_of_files = glob.glob(f'{RAW_DATA_DIR}/*.csv')
    if not list_of_files:
        print("No raw data files found.")
        sys.exit(1)
    
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Transforming file: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        
        # Convert timestamps
        df['dt_txt'] = pd.to_datetime(df['dt_txt'])
        df['collection_time'] = pd.to_datetime(df['collection_time'])
        
        # Sort by time
        df = df.sort_values('dt_txt')
        
        # --- Feature Engineering ---
        
        # 1. Time-based features
        df['hour'] = df['dt_txt'].dt.hour
        df['day_of_week'] = df['dt_txt'].dt.dayofweek
        df['month'] = df['dt_txt'].dt.month
        
        # 2. Lag features (Previous hour)
        # Since this is forecast data, 'dt_txt' are future steps. 
        # But if we treat this as a time series of observations:
        df['temp_lag_1'] = df['temp'].shift(1)
        df['humidity_lag_1'] = df['humidity'].shift(1)
        
        # 3. Rolling statistics (Window of 3)
        df['temp_rolling_mean_3'] = df['temp'].rolling(window=3).mean()
        df['temp_rolling_std_3'] = df['temp'].rolling(window=3).std()
        
        # 4. Target Variable (Next hour temperature)
        df['target_temp'] = df['temp'].shift(-1)
        
        # Drop rows with NaNs created by shifting/rolling
        df_clean = df.dropna()
        
        # Save processed data
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{PROCESSED_DATA_DIR}/weather_processed_{timestamp}.csv"
        
        df_clean.to_csv(output_file, index=False)
        print(f"Transformation complete. Saved to {output_file}")

        # --- Documentation & Logging ---
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment("Weather_Data_Profiling")
        
        with mlflow.start_run():
            print("Generating Pandas Profiling report...")
            profile = ProfileReport(df_clean, title="Weather Data Profiling Report")
            report_path = f"{PROCESSED_DATA_DIR}/profile_report_{timestamp}.html"
            profile.to_file(report_path)
            
            print(f"Logging report to MLflow: {report_path}")
            mlflow.log_artifact(report_path)

        
    except Exception as e:
        print(f"Transformation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    transform_data()
