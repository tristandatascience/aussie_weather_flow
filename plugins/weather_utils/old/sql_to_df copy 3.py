import os
from airflow.exceptions import AirflowException
from weather_utils.postgres_functions import get_postgres_engine, execute_sql_query, save_dataframe, print_dataframe_info
import os

TEMP_PATH = './temp/'

def load_sql_to_df(pgsql_table):
    """Retrieves data from the 'weather_data' table and returns it as a DataFrame."""
    try:
        engine = get_postgres_engine()
        if engine is None:
            return None

        sql_query = f"SELECT * FROM {pgsql_table}"
        df = execute_sql_query(engine, sql_query)
        if df is None:
            return None

        filepath = os.path.join(TEMP_PATH, f"{pgsql_table}.pkl")
        save_dataframe(df, filepath)
        print_dataframe_info(df)
        engine.dispose()
        return df

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None



weather_table = 'weather_data_w_clean'
location_mapping_table = 'location_mapping'
for t in [weather_table,location_mapping_table ]:
    try:
        load_sql_to_df(t,TEMP_PATH)
    except Exception as e:
            print(f"Error load_sql_to_df: {e}")

