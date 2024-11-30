# load_sql_to_df_task.py (Modified version of your other script)
import os
from airflow.exceptions import AirflowException
from weather_utils.postgres_functions import get_postgres_engine, execute_sql_query, save_dataframe, print_dataframe_info
import os

DATA_PATH = './data/pandas'
TEMP_PATH = './temp/'

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