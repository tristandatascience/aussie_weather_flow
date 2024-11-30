import pandas as pd
import os
from sqlalchemy import text
from airflow.providers.postgres.hooks.postgres import PostgresHook
import datetime

# Define paths
DATA_PATH = './data/dataframes'
TEMP_PATH = './temp/'
AIRFLOW_CONN_WEATHER_DATA_POSTGRES='postgresql+psycopg2://airflow:airflow@postgres:5432/weather_data'


def get_postgres_engine(conn_id='weather_data_postgres'):
    """Creates and returns a SQLAlchemy engine object for the PostgreSQL connection."""
    try:
        postgres_hook = PostgresHook(postgres_conn_id=conn_id)
        engine = postgres_hook.get_sqlalchemy_engine()
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        return None


def execute_sql_query(engine, query):
    """Executes a SQL query and returns the result as a DataFrame."""
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None


def save_dataframe(df, filepath):
    """Saves the DataFrame to a pickle file."""
    try:
        df.to_pickle(filepath)
        print(f"DataFrame saved to: {filepath}")
    except Exception as e:
        print(f"Error saving DataFrame: {e}")


def print_dataframe_info(df):
    """Prints DataFrame information (head and info)."""
    try:
        print(df.head())
        print(df.info())
    except Exception as e:
        print(f"Error printing DataFrame information: {e}")


def load_sql_to_df():
    """Retrieves data from the 'weather_data' table and returns it as a DataFrame."""
    try:
        engine = get_postgres_engine()
        if engine is None:
            return None

        sql_query = "SELECT * FROM weather_data_w_clean"
        df = execute_sql_query(engine, sql_query)
        if df is None:
            return None

        filepath = os.path.join(TEMP_PATH, "df.pkl")
        save_dataframe(df, filepath)

        print_dataframe_info(df)

        engine.dispose()
        return df

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None