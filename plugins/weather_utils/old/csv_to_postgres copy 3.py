# load_csv_to_postgres_task.py (Modified version of your original script)
from airflow.exceptions import AirflowException
from weather_utils.postgres_functions import get_postgres_engine, read_csv_file, load_dataframe_to_postgres
import sqlalchemy
import os
import pandas as pd 
from airflow.providers.postgres.hooks.postgres import PostgresHook


#def load_dataframe_to_postgres(df, table_name, engine, if_exists='replace', index=False, dtype=None):
#    """Helper function to load a DataFrame to PostgreSQL."""
#    try:
#        df.to_sql(
#            name=table_name
#            ,con=engine
#            ,if_exists=if_exists
#            ,index=index
#            #,dtype=dtype
#        )
#    except Exception as e:
#        raise AirflowException(f"Failed to load data to {table_name}: {e}")

def load_csv_to_postgres():
    """Loads data from a CSV file to a PostgreSQL table."""
    weather_csv_file_path = './data/w_clean.csv'
    location_csv_file_path = './data/w_clean.csv'
    weather_table = 'weather_data_w_clean'
    location_mapping_table = 'location_mapping'
    try:
        if not os.path.exists(weather_csv_file_path):
            raise FileNotFoundError(f"The file {weather_csv_file_path} does not exist.")
        if not os.path.exists(location_csv_file_path):
            raise FileNotFoundError(f"The file {location_csv_file_path} does not exist.")
        dfw = read_csv_file(weather_csv_file_path, sep=',')
        dfl = read_csv_file(location_csv_file_path, sep=',')

        if dfw is None:
            raise AirflowException("Failed to read dfw file.")
        if dfl is None:
            raise AirflowException("Failed to read dfl file.")

        engine = get_postgres_engine()

        if engine is None:
            raise AirflowException("Failed to get PostgreSQL engine.")

        dtype = {
            'date': sqlalchemy.types.Date(),
            'temperature': sqlalchemy.types.Float(),
            # ... add other column types
        }
        load_dataframe_to_postgres(dfw, weather_table, engine, if_exists='replace', index=False)
        
        load_dataframe_to_postgres(
                    dfl, 
                    location_mapping_table,
                    engine, 
                    if_exists='replace', 
                    index=False
                )        
                
        engine.dispose()

    except AirflowException as e:
        raise e
    except Exception as e:
        raise AirflowException(f"An unexpected error occurred: {e}")