# MLOps Real-Time Predictive System (RPS)

A comprehensive MLOps project for real-time weather forecasting, featuring automated data ingestion, continuous model training, and a modern React dashboard.

## 🏗️ Architecture

- **Orchestration**: Apache Airflow
- **Data Storage**: MinIO (S3-compatible) & DVC
- **Experiment Tracking**: MLflow & Dagshub
- **Model Serving**: FastAPI (Dockerized)
- **Monitoring**: Prometheus & Grafana
- **Frontend**: React + Vite + TailwindCSS

## 🚀 Getting Started

### Prerequisites

- Docker Desktop (ensure it's running)
- Node.js & npm
- Git

### 1. Infrastructure Setup

Start all backend services using Docker Compose:

```bash
docker-compose up -d
```

_This spins up Airflow, MinIO, MLflow, Prometheus, Grafana, and the API._

### 2. Frontend Setup

Navigate to the frontend directory and start the development server:

```bash
cd frontend
npm run dev
```

Access the dashboard at `http://localhost:5173`.

### 3. Accessing Services

| Service      | URL                        | Credentials (User/Pass) |
| ------------ | -------------------------- | ----------------------- |
| **Frontend** | http://localhost:5173      | N/A                     |
| **Airflow**  | http://localhost:8080      | airflow / airflow       |
| **MLflow**   | http://localhost:5000      | N/A                     |
| **MinIO**    | http://localhost:9001      | minioadmin / minioadmin |
| **Grafana**  | http://localhost:3000      | admin / admin           |
| **API**      | http://localhost:8000/docs | N/A                     |

## 🛠️ External Platform Setup

### Dagshub (Remote MLflow/DVC)

1. Create an account on [Dagshub](https://dagshub.com/).
2. Create a new repository.
3. In `models/train.py` and `api/app/main.py`, update `MLFLOW_TRACKING_URI` with your Dagshub remote URL.
4. Set `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` environment variables in `docker-compose.yml` or `.env`.

### Docker Hub (Container Registry)

1. Create an account on [Docker Hub](https://hub.docker.com/).
2. Login locally: `docker login`.
3. Tag and push your API image:
   ```bash
   docker build -t yourusername/rps-api:v1 ./api
   docker push yourusername/rps-api:v1
   ```

## 📊 Monitoring

- **Prometheus** scrapes metrics from the API at `/metrics`.
- **Grafana** is pre-configured to visualize these metrics. Login and explore the dashboards.

## 🧪 Testing

Run the Airflow DAG manually to test the pipeline:

1. Go to Airflow UI (localhost:8080).
2. Enable `weather_etl_dag`.
3. Trigger the DAG.
