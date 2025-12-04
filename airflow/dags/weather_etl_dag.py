from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path
sys.path.append("/opt/airflow/dags/scripts")
from extract import fetch_weather_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_etl_dag',
    default_args=default_args,
    description='ETL pipeline for weather data',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['weather', 'mlops'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_weather_data',
        python_callable=fetch_weather_data,
    )

    # Validation Task
    from validate import validate_data
    validate_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    # Transformation Task
    from transform import transform_data
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )
    
    # DVC Push Task
    # We need to set the working directory to the project root where .dvc exists
    dvc_push_task = BashOperator(
        task_id='dvc_push',
        bash_command='cd /opt/airflow/project && dvc remote add -f origin https://dagshub.com/HaroonNU2555/mlops-project.dvc && dvc remote modify origin --local auth basic && dvc remote modify origin --local user $MLFLOW_TRACKING_USERNAME && dvc remote modify origin --local password $MLFLOW_TRACKING_PASSWORD && dvc add airflow/dags/data/processed && dvc push -r origin',
    )

    # Model Retraining Task
    train_model_task = BashOperator(
        task_id='train_model',
        bash_command='cd /opt/airflow/project && python models/train.py',
    )

    extract_task >> validate_task >> transform_task >> [dvc_push_task, train_model_task]
