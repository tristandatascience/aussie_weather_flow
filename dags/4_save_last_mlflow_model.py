from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

# Import functions from meteo_functions
from weather_utils.mlflow_functions import  export_last_model
import os
# Define paths
MODEL_PATH = "/opt/airflow/models/"
ACTUAL_MODEL_PATH = os.path.join(MODEL_PATH, "actual_model.joblib")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(dag_id="save_last_mlflow_model",
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["model_export"]
)

with dag:
    
    export_best_model_task = PythonOperator(
        task_id="export_last_model",
        python_callable=export_last_model,
    )

    export_last_model