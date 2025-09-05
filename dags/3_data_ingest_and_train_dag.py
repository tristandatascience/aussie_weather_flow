from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

# Import functions from meteo_functions
from weather_utils.model_functions import train_and_save_model, load_df
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.convert_to_one_csv import convert
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.mlflow_functions import prepare_data, train_model, get_best_model
from weather_utils.acquire_data import acquire
from weather_utils.prepare_data import cleaning


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

combined_dag = DAG(
    dag_id="data_ingest_and_train_dag",
    schedule=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["data_ingestion", "model_training"],
)

with combined_dag:

    # Data Ingestion Tasks
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

    # Model Training Tasks
    load_sql_to_df_task = PythonOperator(
        task_id="load_sql_to_df",
        python_callable=load_sql_to_df,
    )

    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    # Define the order of tasks
    (
        scrap_data_task >>
        scrap_to_csv_task >>
        prepare_data_task >>
        load_csv_to_postgres_task >>
        load_sql_to_df_task >>
        train_model_task
    )