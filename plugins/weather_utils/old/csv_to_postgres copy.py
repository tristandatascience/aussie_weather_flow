import os
import pandas as pd
from airflow.hooks.postgres_hook import PostgresHook
from airflow.exceptions import AirflowException
import sqlalchemy

def load_csv_to_postgres():
    csv_file_path = './data/w_clean.csv'

    try:
        # Vérifier si le fichier existe
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"Le fichier {csv_file_path} n'existe pas.")


        df = pd.read_csv(csv_file_path, sep=',')

        postgres_hook = PostgresHook(postgres_conn_id='weather_data_postgres')
        engine = postgres_hook.get_sqlalchemy_engine()

        # Définir les types de données (à adapter à vos données)
        dtype = {
            'date': sqlalchemy.types.Date(),
            'temperature': sqlalchemy.types.Float(),
            #etc
        }

        with engine.connect() as connexion: 
            df.to_sql('weather_data_w_clean', connexion, if_exists='replace', index=False)

        engine.dispose()

        print("Données chargées avec succès.")

    except (FileNotFoundError, pd.errors.ParserError, sqlalchemy.exc.SQLAlchemyError) as e:
        raise AirflowException(f"Erreur lors du chargement : {e}")