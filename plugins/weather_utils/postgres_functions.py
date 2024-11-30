# shared_functions.py
import os
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException
import sqlalchemy

def get_postgres_engine(conn_id='weather_data_postgres'):
    """Creates and returns a SQLAlchemy engine object for the PostgreSQL connection."""
    try:
        postgres_hook = PostgresHook(postgres_conn_id=conn_id)
        engine = postgres_hook.get_sqlalchemy_engine()
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        return None

def read_csv_file(csv_file_path, **kwargs):
    """Reads a CSV file into a Pandas DataFrame."""
    try:
        df = pd.read_csv(csv_file_path, **kwargs)
        return df
    except (FileNotFoundError, pd.errors.ParserError) as e:
        print(f"Error reading CSV file: {e}")
        return None

def execute_sql_query(engine, query):
    """Executes a SQL query and returns the result as a DataFrame."""
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None

def load_dataframe_to_postgres(df, table_name, engine, **kwargs):
    """Loads a Pandas DataFrame to a PostgreSQL table."""
    try:
        with engine.connect() as connection:
            df.to_sql(table_name, connection, **kwargs)
        print(f"Data loaded successfully into table: {table_name}")
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Error loading DataFrame to PostgreSQL: {e}")

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