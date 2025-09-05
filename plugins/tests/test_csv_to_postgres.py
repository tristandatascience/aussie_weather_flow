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
         patch('weather_utils.csv_to_postgres.load_dataframe_to_postgres') as mock_load_df, \
         patch('weather_utils.csv_to_postgres.execute_sql_query') as mock_execute_sql:

        mock_df = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'location_id': [1, 2, 3],
            'temperature': [20.5, 22.1, 19.8]
        })
        mock_read_csv.return_value = mock_df

        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_execute_sql.return_value = pd.DataFrame(columns=['date', 'location_id'])
        load_csv_to_postgres()

        mock_read_csv.assert_called_once_with('./data/w_clean.csv', sep=',')
        mock_execute_sql.assert_called_once()
        mock_load_df.assert_called_once_with(
            mock_df,
            'weather_data_w_clean',
            mock_engine,
            if_exists='append',
            index=False
        )
        mock_engine.dispose.assert_called_once()

def test_load_csv_to_postgres_with_error():
    with patch('weather_utils.csv_to_postgres.os.path.exists', return_value=False):
        with pytest.raises(AirflowException) as exc_info:
            load_csv_to_postgres()
        assert "The file ./data/w_clean.csv does not exist" in str(exc_info.value)