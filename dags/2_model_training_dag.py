from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import os

# Import functions from meteo_functions
from weather_utils.model_functions import train_and_save_model, load_df
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.convert_to_one_csv import convert
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.mlflow_functions import prepare_data, train_model, get_best_model
from weather_utils.acquire_data import acquire
from weather_utils.prepare_data import cleaning

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

dag = DAG(dag_id="model_training_dag",
    schedule_interval=timedelta(days=7),
    start_date=days_ago(1),
    catchup=False,
    tags=["model_training"]
)

with dag:
    
    load_sql_to_df_task = PythonOperator(
        task_id="load_sql_to_df",
        python_callable=load_sql_to_df,
    )
    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )
    load_sql_to_df_task >> train_model_task