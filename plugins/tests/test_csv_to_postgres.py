import pytest
from unittest.mock import patch, MagicMock
from weather_utils.csv_to_postgres import load_csv_to_postgres
from airflow.exceptions import AirflowException
import pandas as pd
import sqlalchemy

def test_load_csv_to_postgres():
    with patch('weather_utils.csv_to_postgres.os.path.exists', return_value=True), \
         patch('weather_utils.csv_to_postgres.read_csv_file') as mock_read_csv, \
         patch('weather_utils.csv_to_postgres.get_postgres_engine') as mock_get_engine, \
         patch('weather_utils.csv_to_postgres.load_dataframe_to_postgres') as mock_load_df:

        # Simuler un DataFrame
        mock_df = pd.DataFrame({'test': [1, 2, 3]})
        mock_read_csv.return_value = mock_df

        # Simuler l'engine PostgreSQL
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        # Exécuter la fonction
        load_csv_to_postgres()

        # Vérifier les appels
        mock_read_csv.assert_called_once_with('./data/w_clean.csv', sep=',')
        mock_load_df.assert_called_once_with(
            mock_df,
            'weather_data_w_clean',
            mock_engine,
            if_exists='replace',
            index=False
        )
        mock_engine.dispose.assert_called_once()

def test_load_csv_to_postgres_with_error():
    with patch('weather_utils.csv_to_postgres.os.path.exists', return_value=False):
        with pytest.raises(AirflowException) as exc_info:
            load_csv_to_postgres()
        assert "The file ./data/w_clean.csv does not exist" in str(exc_info.value)