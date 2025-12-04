import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
import os
import glob

# Constants
PROCESSED_DATA_PATH = "/opt/airflow/dags/data/processed" # Path inside Docker container
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

def load_data():
    # Find all processed files
    list_of_files = glob.glob(f'{PROCESSED_DATA_PATH}/*.csv')
    if not list_of_files:
        print("No processed data files found. Generating synthetic data for testing.")
        # Generate synthetic data with features
        df = pd.DataFrame({
            'temp': np.random.normal(20, 5, 100),
            'humidity': np.random.uniform(30, 90, 100),
            'pressure': np.random.normal(1013, 5, 100),
            'wind_speed': np.random.uniform(0, 20, 100),
            'clouds_all': np.random.randint(0, 100, 100),
            'hour': np.random.randint(0, 24, 100),
            'day_of_week': np.random.randint(0, 7, 100),
            'month': np.random.randint(1, 12, 100),
            'temp_lag_1': np.random.normal(20, 5, 100),
            'temp_rolling_mean_3': np.random.normal(20, 5, 100),
            'temp_rolling_std_3': np.random.uniform(0, 2, 100),
            'target_temp': np.random.normal(20, 5, 100)
        })
        return df
    
    print(f"Loading data from {len(list_of_files)} files.")
    # Concatenate all files
    df_list = [pd.read_csv(file) for file in list_of_files]
    df = pd.concat(df_list, ignore_index=True)
    
    return df

def train_model():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("Weather_Prediction_RPS")
    
    df = load_data()
    
    # Features from transformation step
    features = [
        'temp', 'humidity', 'pressure', 'wind_speed', 'clouds_all',
        'hour', 'day_of_week', 'month',
        'temp_lag_1', 'temp_rolling_mean_3', 'temp_rolling_std_3'
    ]
    target = 'target_temp'
    
    # Ensure columns exist
    available_features = [f for f in features if f in df.columns]
    if len(available_features) < len(features):
        print(f"Warning: Missing features. Available: {available_features}")
    
    X = df[available_features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    with mlflow.start_run():
        # Hyperparameters
        n_estimators = 100
        max_depth = 10
        
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        
        # Train model
        model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        print(f"RMSE: {rmse}")
        print(f"MAE: {mae}")
        print(f"R2: {r2}")
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        
        # Log model and register it
        mlflow.sklearn.log_model(
            sk_model=model, 
            artifact_path="model",
            registered_model_name="Production"
        )
        print("Model trained, logged, and registered to MLflow")

if __name__ == "__main__":
    train_model()
