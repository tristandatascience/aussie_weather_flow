import pandas as pd
import os
from sqlalchemy import text
from airflow.providers.postgres.hooks.postgres import PostgresHook
import datetime

# Define paths
DATA_PATH = './data/dataframes'
TEMP_PATH = './temp/'
AIRFLOW_CONN_WEATHER_DATA_POSTGRES='postgresql+psycopg2://airflow:airflow@postgres:5432/weather_data'


def load_sql_to_df():
    """Récupère les données de la table 'weather_data' et les retourne en DataFrame."""
    try:
        # Établir une connexion à PostgreSQL via PostgresHook
        postgres_hook = PostgresHook(postgres_conn_id='weather_data_postgres')
        engine = postgres_hook.get_sqlalchemy_engine()

        # Requête SQL pour récupérer toutes les données de la table
        sql_query = "SELECT * FROM weather_data_w_clean"

        # Lire les données dans un DataFrame
        df = pd.read_sql_query(sql_query, engine)
        df.to_pickle(os.path.join(TEMP_PATH, "df.pkl"))
        print(df.head()) #Affiche les 5 premières lignes du DataFrame
        print(df.info()) #Affiche des informations sur le DataFrame
        # Fermer la connexion
        engine.dispose()

        return df

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return None
    