# load_csv_to_postgres_task.py (Modified version of your original script)
from airflow.exceptions import AirflowException
from weather_utils.postgres_functions import get_postgres_engine, read_csv_file, load_dataframe_to_postgres
import sqlalchemy
import os
import pandas as pd 
from airflow.providers.postgres.hooks.postgres import PostgresHook


def load_csv_to_postgres():
    """Loads data from a CSV file to a PostgreSQL table."""
    csv_file_path = './data/w_clean.csv'
    table_name = 'weather_data_w_clean'

    try:
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"The file {csv_file_path} does not exist.")

        df = read_csv_file(csv_file_path, sep=',')
        if df is None:
            raise AirflowException("Failed to read CSV file.")
        df['ingestion_date'] = pd.Timestamp.now().date()
        engine = get_postgres_engine()
        if engine is None:
            raise AirflowException("Failed to get PostgreSQL engine.")

        dtype = {
            'date': sqlalchemy.types.Date(),
            'temperature': sqlalchemy.types.Float(),
            # ... add other column types
        }
        load_dataframe_to_postgres(df, table_name, engine, if_exists='append', index=False)
        engine.dispose()

    except AirflowException as e:
        raise e
    except Exception as e:
        raise AirflowException(f"An unexpected error occurred: {e}")