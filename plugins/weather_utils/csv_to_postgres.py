# load_csv_to_postgres_task.py (Modified version of your original script)
from airflow.exceptions import AirflowException
from weather_utils.postgres_functions import get_postgres_engine, read_csv_file, load_dataframe_to_postgres, execute_sql_query
import sqlalchemy
import os
import pandas as pd 
from airflow.providers.postgres.hooks.postgres import PostgresHook


def remove_existing_data(df, table_name, engine):
    """Supprime les doublons existants du DataFrame avant insertion."""
    try:
        # Créer une copie du DataFrame pour éviter de modifier l'original
        df_filtered = df.copy()
        
        # On suppose que 'date' et 'location_id' identifient de manière unique une donnée
        if 'date' in df.columns and 'location_id' in df.columns:
            # Récupérer les données existantes dans la table
            existing_query = f"SELECT date, location_id FROM {table_name}"
            existing_data = execute_sql_query(engine, existing_query)
            
            if existing_data is not None and not existing_data.empty:
                # Créer une condition pour filtrer les doublons
                # On ne garde que les lignes qui n'existent pas déjà dans la table
                df_filtered = df_filtered[~(
                    df_filtered['date'].isin(existing_data['date']) &
                    df_filtered['location_id'].isin(existing_data['location_id'])
                )]
                return df_filtered
        
        # Si pas de colonnes d'identification claires, retourner le DataFrame original
        # Dans un cas réel, on pourrait implémenter une logique plus complexe
        return df
        
    except Exception as e:
        print(f"Error removing existing data: {e}")
        return df  # En cas d'erreur, retourner le DataFrame original

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
        
        # Vérifier les doublons et ne charger que les nouvelles données
        df_to_insert = remove_existing_data(df, table_name, engine)
        
        if not df_to_insert.empty:
            load_dataframe_to_postgres(df_to_insert, table_name, engine, if_exists='append', index=False)
            print(f"Added {len(df_to_insert)} new records to {table_name}")
        else:
            print(f"No new records to add to {table_name}")
        
        engine.dispose()

    except AirflowException as e:
        raise e
    except Exception as e:
        raise AirflowException(f"An unexpected error occurred: {e}")