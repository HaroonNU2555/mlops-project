# 🌤️ MLOps Real-Time Predictive System (RPS)

A comprehensive end-to-end MLOps project for real-time weather forecasting, featuring automated data pipelines, continuous model training, experiment tracking, and production monitoring.

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Quick Start](#-quick-start)
- [Phase I: Orchestration Core (Apache Airflow)](#-phase-i-orchestration-core-apache-airflow)
- [Phase II: Experimentation & Model Management](#-phase-ii-experimentation--model-management)
- [Phase III: CI/CD Pipeline](#-phase-iii-cicd-pipeline)
- [Phase IV: Monitoring & Observability](#-phase-iv-monitoring--observability)
- [Service Endpoints](#-service-endpoints)

---

## 🏗️ Architecture Overview

| Component               | Technology            | Purpose                                   |
| ----------------------- | --------------------- | ----------------------------------------- |
| **Orchestration**       | Apache Airflow        | DAG-based ETL and retraining pipeline     |
| **Data Storage**        | MinIO (S3-compatible) | Cloud-like object storage                 |
| **Data Versioning**     | DVC + Dagshub         | Dataset version control                   |
| **Experiment Tracking** | MLflow + Dagshub      | Hyperparameters, metrics, model artifacts |
| **Model Serving**       | FastAPI (Dockerized)  | REST API for predictions                  |
| **Monitoring**          | Prometheus + Grafana  | Metrics, dashboards, alerting             |
| **CI/CD**               | GitHub Actions + CML  | Automated testing, training, deployment   |
| **Frontend**            | React + Vite          | User dashboard                            |

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (running)
- Python 3.9+
- Git

### Start All Services

```bash
docker-compose up -d
```

### Access Points

| Service         | URL                           | Credentials             |
| --------------- | ----------------------------- | ----------------------- |
| **Airflow**     | http://localhost:8080         | airflow / airflow       |
| **MLflow**      | http://localhost:5000         | N/A                     |
| **MinIO**       | http://localhost:9001         | minioadmin / minioadmin |
| **Grafana**     | http://localhost:3000         | admin / admin           |
| **Prometheus**  | http://localhost:9090         | N/A                     |
| **API Docs**    | http://localhost:8000/docs    | N/A                     |
| **API Metrics** | http://localhost:8000/metrics | N/A                     |
| **Frontend**    | http://localhost:5173         | N/A                     |

---

## 📦 Phase I: Orchestration Core (Apache Airflow)

> **Requirement**: MLOps pipeline structured as a DAG running on schedule for ETL and model retraining.

### 📍 Demonstration Endpoint

- **Airflow UI**: http://localhost:8080
- **DAG Name**: `weather_etl_dag`
- **DAG File**: [`airflow/dags/weather_etl_dag.py`](airflow/dags/weather_etl_dag.py)

### ✅ Requirements Satisfied

#### 1. Extraction (2.1)

| Requirement                      | Implementation                                   | Location                                                             |
| -------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------- |
| Connect to API & fetch live data | `PythonOperator` calls OpenWeatherMap API        | `extract_task` in DAG                                                |
| Save raw data with timestamp     | Saves to `/data/raw/weather_YYYYMMDD_HHMMSS.csv` | [`airflow/dags/scripts/extract.py`](airflow/dags/scripts/extract.py) |

#### 2. Mandatory Quality Gate

| Requirement                         | Implementation                           | Location                                                                         |
| ----------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| Data quality check after extraction | Validates null values <1% and schema     | `quality_check_task` in DAG                                                      |
| Fail DAG if quality fails           | Raises `AirflowFailException` on failure | [`airflow/dags/scripts/quality_check.py`](airflow/dags/scripts/quality_check.py) |

#### 3. Transformation (2.2)

| Requirement         | Implementation                              | Location                                                                 |
| ------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| Clean raw data      | Handles missing values, outliers            | `transform_task` in DAG                                                  |
| Feature engineering | Lag features, rolling means, time encodings | [`airflow/dags/scripts/transform.py`](airflow/dags/scripts/transform.py) |

**Features Created:**

- `hour`, `day_of_week`, `month` (time encodings)
- `temp_lag_1` (lag feature)
- `temp_rolling_mean_3`, `temp_rolling_std_3` (rolling statistics)

#### 4. Documentation Artifact

| Requirement                  | Implementation                            | Location             |
| ---------------------------- | ----------------------------------------- | -------------------- |
| Generate data quality report | Uses `ydata-profiling` (Pandas Profiling) | `transform.py`       |
| Log to MLflow/Dagshub        | Report logged as artifact                 | Visible in MLflow UI |

#### 5. Loading & Versioning (2.3 & 3)

| Requirement                   | Implementation                      | Location                     |
| ----------------------------- | ----------------------------------- | ---------------------------- |
| Store in cloud object storage | Processed data saved to MinIO       | `load_task` in DAG           |
| DVC versioning                | `.dvc` file tracks dataset versions | [`.dvc/config`](.dvc/config) |
| Push to remote storage        | DVC pushes to Dagshub               | `dvc_push_task` in DAG       |

---

## 🧪 Phase II: Experimentation & Model Management

> **Requirement**: MLflow tracking with Dagshub as central hub for Code, Data, and Models.

### 📍 Demonstration Endpoints

- **MLflow UI (Local)**: http://localhost:5000
- **Dagshub (Remote)**: https://dagshub.com/HaroonNU2555/mlops-project
- **Training Script**: [`models/train.py`](models/train.py)

### ✅ Requirements Satisfied

#### MLflow Tracking

| Requirement                 | Implementation                          | Location   |
| --------------------------- | --------------------------------------- | ---------- |
| Track experiment runs       | `mlflow.start_run()` context            | `train.py` |
| Log hyperparameters         | `mlflow.log_param("n_estimators", 100)` | `train.py` |
| Log metrics (RMSE, MAE, R²) | `mlflow.log_metric("rmse", rmse)`       | `train.py` |
| Log trained model           | `mlflow.sklearn.log_model()`            | `train.py` |

**Tracked Metrics:**

```python
mlflow.log_metric("rmse", rmse)   # Root Mean Square Error
mlflow.log_metric("mae", mae)     # Mean Absolute Error
mlflow.log_metric("r2", r2)       # R-squared Score
```

#### Dagshub as Central Hub

| Component           | Integration                              |
| ------------------- | ---------------------------------------- |
| **Code (Git)**      | GitHub repo linked to Dagshub            |
| **Data (DVC)**      | DVC remote configured to Dagshub storage |
| **Models (MLflow)** | `MLFLOW_TRACKING_URI` points to Dagshub  |

**Environment Configuration (`.env`):**

```env
MLFLOW_TRACKING_URI=https://dagshub.com/HaroonNU2555/mlops-project.mlflow
MLFLOW_TRACKING_USERNAME=HaroonNU2555
MLFLOW_TRACKING_PASSWORD=<token>
DAGSHUB_REPO_URL=https://dagshub.com/HaroonNU2555/mlops-project.dvc
```

---

## 🔄 Phase III: CI/CD Pipeline

> **Requirement**: Professional branching strategy with automated checks using GitHub Actions and CML.

### 📍 Demonstration Endpoints

- **GitHub Actions**: https://github.com/HaroonNU2555/mlops-project/actions
- **Workflow File**: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)
- **Docker Hub**: https://hub.docker.com/r/haroonnu2555/weather-prediction-api

### ✅ Requirements Satisfied

#### Git Workflow (5.1 & 5.3)

| Requirement            | Implementation                              |
| ---------------------- | ------------------------------------------- |
| Strict branching model | `dev`, `test`, `master` branches configured |
| Feature branches       | All work starts on `feature/*` branches     |
| Mandatory PR approvals | Branch protection rules require 1 approval  |

**Branch Flow:**

```
feature/* → dev → test → master
     ↓         ↓        ↓
  (work)   (PR+CI)  (PR+CI+Deploy)
```

#### GitHub Actions with CML (5.1 & 5.2)

| Merge Event       | CI Action                                 | CML Integration                         |
| ----------------- | ----------------------------------------- | --------------------------------------- |
| **Feature → dev** | ✅ Linting (flake8) + Unit Tests (pytest) | N/A                                     |
| **dev → test**    | ✅ Model Retraining                       | ✅ Posts metric comparison report to PR |
| **test → master** | ✅ Production Deployment                  | N/A                                     |

**CML Report Features:**

- Compares new model RMSE vs production baseline
- Posts markdown report to PR comments
- **Blocks merge if new model performs worse**

#### Containerization (5.4 & 5.5)

| Requirement               | Implementation                           | Location                           |
| ------------------------- | ---------------------------------------- | ---------------------------------- |
| REST API in Docker        | FastAPI app in container                 | [`api/Dockerfile`](api/Dockerfile) |
| Semantic versioning       | `v1.YYYYMMDD.RUN_NUMBER` tags            | CI/CD workflow                     |
| Push to Docker Hub        | `docker push` in deployment job          | GitHub Actions                     |
| Health check verification | Container tested with `/health` endpoint | Deploy job                         |

**API Endpoints:**

```
POST /predict          # Make predictions
GET  /health           # Health check
GET  /metrics          # Prometheus metrics
GET  /docs             # Swagger documentation
```

**Deployment Verification:**

```bash
# Run container locally
docker run -p 8000:8000 haroonnu2555/weather-prediction-api:latest

# Verify health
curl http://localhost:8000/health
# Response: {"status": "healthy", "model_loaded": true}
```

---

## 📊 Phase IV: Monitoring & Observability

> **Requirement**: Prometheus metrics, Grafana dashboards, and alerting for production reliability.

### 📍 Demonstration Endpoints

- **Prometheus**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000
- **API Metrics**: http://localhost:8000/metrics

### ✅ Requirements Satisfied

#### Prometheus Metrics (Embedded in FastAPI)

| Metric                       | Type      | Description                       |
| ---------------------------- | --------- | --------------------------------- |
| `predictions_total`          | Counter   | Total prediction requests         |
| `prediction_latency_seconds` | Histogram | Inference latency (p50, p95, p99) |
| `prediction_errors_total`    | Counter   | Failed predictions                |
| `out_of_distribution_ratio`  | Gauge     | Data drift proxy (OOD ratio)      |
| `feature_mean_shift`         | Gauge     | Per-feature z-score from training |

**Implementation**: [`api/app/main.py`](api/app/main.py)

#### Grafana Dashboard

| Panel                 | Visualization | Purpose                        |
| --------------------- | ------------- | ------------------------------ |
| Total Predictions     | Stat          | Request volume                 |
| Avg Inference Latency | Stat          | Performance indicator          |
| Total Errors          | Stat          | Error tracking                 |
| Latency Over Time     | Time Series   | p50, p95, p99 trends           |
| Request Rate          | Time Series   | Throughput monitoring          |
| OOD Ratio Gauge       | Gauge         | Data drift indicator           |
| Data Drift Over Time  | Time Series   | Drift trends                   |
| Feature Z-Scores      | Bar Chart     | Per-feature distribution shift |

**Dashboard File**: [`monitoring/grafana/provisioning/dashboards/mlops-dashboard.json`](monitoring/grafana/provisioning/dashboards/mlops-dashboard.json)

#### Alerting Rules

| Alert                      | Condition                | Severity    | Action             |
| -------------------------- | ------------------------ | ----------- | ------------------ |
| **High Inference Latency** | p95 > 500ms for 2min     | ⚠️ Warning  | Fires notification |
| **Data Drift Detected**    | OOD ratio > 50% for 5min | 🔴 Critical | Fires notification |
| **High Error Rate**        | Error rate > 10%         | 🔴 Critical | Fires notification |

**Alerting Config**: [`monitoring/grafana/provisioning/alerting/alerts.yml`](monitoring/grafana/provisioning/alerting/alerts.yml)

---

## 🧪 Testing the Pipeline

### 1. Trigger the Airflow DAG

```bash
# Open Airflow UI
open http://localhost:8080

# Enable and trigger 'weather_etl_dag'
```

### 2. Make a Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "temp": 20.5,
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 5.2,
    "clouds_all": 40,
    "hour": 14,
    "day_of_week": 3,
    "month": 12,
    "temp_lag_1": 19.8,
    "temp_rolling_mean_3": 20.1,
    "temp_rolling_std_3": 0.8
  }'
```

### 3. View Metrics

```bash
curl http://localhost:8000/metrics
```

### 4. Check Grafana Dashboard

Open http://localhost:3000 and view the "Weather Prediction MLOps Dashboard"

---

## 📁 Project Structure

```
├── .github/workflows/ci-cd.yml    # GitHub Actions pipeline
├── airflow/
│   └── dags/
│       ├── weather_etl_dag.py     # Main DAG
│       └── scripts/
│           ├── extract.py         # Data extraction
│           ├── quality_check.py   # Quality gate
│           └── transform.py       # Feature engineering
├── api/
│   ├── Dockerfile                 # API container
│   └── app/main.py               # FastAPI application
├── models/
│   └── train.py                  # Model training script
├── monitoring/
│   ├── prometheus/prometheus.yml  # Prometheus config
│   └── grafana/provisioning/     # Grafana dashboards & alerts
├── docker-compose.yml            # Infrastructure setup
├── .dvc/config                   # DVC configuration
└── .env                          # Environment variables
```

---

## 🔗 External Platform Links

| Platform       | Purpose             | URL                                                          |
| -------------- | ------------------- | ------------------------------------------------------------ |
| **Dagshub**    | MLflow + DVC Hub    | https://dagshub.com/HaroonNU2555/mlops-project               |
| **GitHub**     | Source Code + CI/CD | https://github.com/HaroonNU2555/mlops-project                |
| **Docker Hub** | Container Registry  | https://hub.docker.com/r/haroonnu2555/weather-prediction-api |

---

## 📝 License

This project is developed as part of the MLOps course curriculum.
