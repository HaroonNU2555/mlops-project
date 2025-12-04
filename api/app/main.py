from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import mlflow.sklearn
import os
import numpy as np
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Weather Prediction RPS", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency in seconds')
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Prediction errors')

# Drift Metrics
OOD_RATIO = Gauge('out_of_distribution_ratio', 'Ratio of OOD feature values')
FEATURE_MEAN_SHIFT = Gauge('feature_mean_shift', 'Mean shift from training distribution', ['feature_name'])

# Model Loading
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
# Load the model from the "Production" stage
MODEL_URI = os.getenv("MODEL_URI", "models:/Production/Production")

model = None
training_stats = {} # Store training stats for drift detection

@app.on_event("startup")
def load_model():
    global model, training_stats
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        model = mlflow.sklearn.load_model(MODEL_URI)
        print("Model loaded successfully from MLflow")
        
        # In a real system, we would load training stats (mean/std) from an artifact
        # For now, we initialize with dummy values or try to fetch from MLflow run
        training_stats = {
            'temp': {'mean': 20.0, 'std': 5.0},
            'humidity': {'mean': 60.0, 'std': 15.0}
        }
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Model not loaded. API will fail on predict.")

class PredictionRequest(BaseModel):
    temp: float
    humidity: float
    pressure: float
    wind_speed: float
    clouds_all: float
    hour: int
    day_of_week: int
    month: int
    temp_lag_1: float
    temp_rolling_mean_3: float
    temp_rolling_std_3: float

class PredictionResponse(BaseModel):
    predicted_temp: float

@app.get("/health")
def health_check():
    if model:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    PREDICTION_COUNT.inc()
    with PREDICTION_LATENCY.time():
        try:
            if not model:
                raise HTTPException(status_code=503, detail="Model not loaded")

            # Prepare features
            features = pd.DataFrame([request.dict()])
            
            # Drift Detection (Simple Z-score check)
            ood_count = 0
            for col, stats in training_stats.items():
                if col in features.columns:
                    val = features[col].iloc[0]
                    z_score = abs((val - stats['mean']) / stats['std'])
                    if z_score > 3: # Threshold for OOD
                        ood_count += 1
                    
                    # Update mean shift gauge
                    FEATURE_MEAN_SHIFT.labels(feature_name=col).set(z_score)
            
            if len(training_stats) > 0:
                OOD_RATIO.set(ood_count / len(training_stats))

            prediction = model.predict(features)[0]
            
            return {"predicted_temp": prediction}
        except Exception as e:
            PREDICTION_ERRORS.inc()
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
