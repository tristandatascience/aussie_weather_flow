# tests/test_sql_to_df.py

import pandas as pd
from unittest.mock import patch, MagicMock
import os
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.postgres_functions import PostgresHook

def test_load_sql_to_df():
  with patch('weather_utils.postgres_functions.PostgresHook') as mock_postgres_hook, \
       patch('pandas.read_sql_query') as mock_read_sql_query, \
       patch('pandas.DataFrame.to_pickle') as mock_to_pickle, \
       patch('os.path.join', return_value='mock_path.pkl'):
      
      # Configurer les mocks
      mock_engine = MagicMock()
      mock_postgres_hook.return_value.get_sqlalchemy_engine.return_value = mock_engine

      sample_data = {'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']}
      sample_df = pd.DataFrame(sample_data)
      mock_read_sql_query.return_value = sample_df

      # Exécuter la fonction
      result = load_sql_to_df()

      # Vérifications
      assert isinstance(result, pd.DataFrame)
      assert not result.empty
      mock_read_sql_query.assert_called_once_with("SELECT * FROM weather_data_w_clean", mock_engine)
      mock_to_pickle.assert_called_once_with('mock_path.pkl')
      mock_engine.dispose.assert_called_once()

      # Vérifier que les prints sont appelés (optionnel, car difficile à tester précisément)
      # Vous pouvez ajouter un mock pour print si nécessaire

  # Test du cas d'erreur
  with patch('weather_utils.postgres_functions.PostgresHook', side_effect=Exception("Test error")):
      result = load_sql_to_df()
      assert result is None