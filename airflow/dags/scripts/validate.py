import pandas as pd
import sys
import os
import glob
from datetime import datetime

# Constants
RAW_DATA_DIR = "/opt/airflow/dags/data/raw"

def validate_data():
    # Find latest file
    list_of_files = glob.glob(f'{RAW_DATA_DIR}/*.csv')
    if not list_of_files:
        print("No data files found to validate.")
        sys.exit(1)
    
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Validating file: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        
        # 1. Check for null values
        if df.isnull().any().any():
            null_counts = df.isnull().sum()
            print("Null values found:")
            print(null_counts[null_counts > 0])
            # Fail if critical columns have nulls
            critical_cols = ['temp', 'humidity', 'pressure', 'wind_speed']
            if df[critical_cols].isnull().any().any():
                print("Critical columns have null values. Validation Failed.")
                sys.exit(1)
        
        # 2. Schema Validation
        expected_cols = ['dt', 'temp', 'humidity', 'pressure', 'wind_speed', 'collection_time']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            print(f"Missing expected columns: {missing_cols}")
            sys.exit(1)
            
        # 3. Freshness Check (e.g., data shouldn't be older than 24 hours)
        # Assuming 'collection_time' is in ISO format
        if 'collection_time' in df.columns:
            latest_time = pd.to_datetime(df['collection_time'].max())
            now = datetime.now()
            age = now - latest_time
            if age.total_seconds() > 86400: # 24 hours
                print(f"Data is too old. Age: {age}")
                # Warning only for now, or fail if strict
                # sys.exit(1) 
        
        print("Data validation passed successfully.")
        
    except Exception as e:
        print(f"Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate_data()
