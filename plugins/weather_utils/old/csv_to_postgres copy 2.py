import os
import pandas as pd
from airflow.hooks.postgres_hook import PostgresHook
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

def load_dataframe_to_postgres(df, table_name, engine, dtype=None, **kwargs):
    """Loads a Pandas DataFrame to a PostgreSQL table."""
    try:
        with engine.connect() as connection:
            df.to_sql(table_name, connection, dtype=dtype, **kwargs)
        print(f"Data loaded successfully into table: {table_name}")
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Error loading DataFrame to PostgreSQL: {e}")

def load_csv_to_postgres():
    """Loads data from a CSV file to a PostgreSQL table."""
    csv_file_path = './data/w_clean.csv'
    table_name = 'weather_data_w_clean'

    try:
        # Check if the file exists
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"The file {csv_file_path} does not exist.")

        df = read_csv_file(csv_file_path, sep=',')
        if df is None:
            raise AirflowException("Failed to read CSV file.")

        engine = get_postgres_engine()
        if engine is None:
            raise AirflowException("Failed to get PostgreSQL engine.")

        # Define data types (adapt to your data)
        dtype = {
            'date': sqlalchemy.types.Date(),
            'temperature': sqlalchemy.types.Float(),
            # ... add other column types
        }

        load_dataframe_to_postgres(df, table_name, engine, dtype=dtype, if_exists='replace', index=False)

        engine.dispose()


    except AirflowException as e:
        raise e
    except Exception as e:
        raise AirflowException(f"An unexpected error occurred: {e}")