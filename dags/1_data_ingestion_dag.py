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

# Import functions from meteo_functions
from weather_utils.model_functions import train_and_save_model
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.convert_to_one_csv import convert
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.model_functions import load_df
from weather_utils.mlflow_functions import  prepare_data, train_model , get_best_model ,export_best_model
from weather_utils.model_functions import train_and_save_model
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.acquire_data import acquire
from weather_utils.convert_to_one_csv import convert
from weather_utils.prepare_data import cleaning
import joblib
from sklearn.metrics import mean_absolute_error, r2_score
import os
import datetime
import numpy as np

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

dag = DAG(
    dag_id="data_ingestion_dag",
    schedule_interval=timedelta(days=1),  
    start_date=days_ago(1),
    catchup=False,
    tags=["data_ingestion"],
)

with dag:

    scrap_data_task = PythonOperator(
        task_id='scrap_data',
        python_callable=acquire,
    )

    scrap_to_csv_task = PythonOperator(
        task_id='scrap_to_csv',
        python_callable=convert,
    )

    prepare_data_task = PythonOperator(
        task_id='prepare_data',
        python_callable=cleaning,
    )

    load_csv_to_postgres_task = PythonOperator(
        task_id='load_csv_to_postgres',
        python_callable=load_csv_to_postgres,
    )
  
    scrap_data_task >> scrap_to_csv_task >> prepare_data_task >> load_csv_to_postgres_task