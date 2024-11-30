# test_convert_to_one_csv.py
import os
import pandas as pd
from unittest.mock import patch, MagicMock, call
from weather_utils.convert_to_one_csv import merge_cvc_dids

def test_merge_cvc_dids():
  data_path = '/fake_data_path'

  # Données simulées pour CodeVilleClimat.csv
  cvc_data = pd.DataFrame({
      'station_id': ['001', '002'],
      'Location': ['Location1', 'Location2'],
      'OtherField': ['Value1', 'Value2']
  })

  # Données simulées pour DataIds.csv
  dids_data = pd.DataFrame({
      'station_id': ['001', '002'],
      'data_id': ['DataID1', 'DataID2']
  })

  with patch('pandas.read_csv') as mock_read_csv:
      # La première fois que read_csv est appelé, il retourne cvc_data
      # La deuxième fois, il retourne dids_data
      mock_read_csv.side_effect = [cvc_data, dids_data]

      # Appel de la fonction à tester
      result_df = merge_cvc_dids(data_path)

      # Vérifications
      expected_df = pd.DataFrame({
          'station_id': ['001', '002'],
          'Location': ['Location1', 'Location2'],
          'OtherField': ['Value1', 'Value2'],
          'data_id': ['DataID1', 'DataID2']
      })

      pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))

      # Vérifier que read_csv a été appelé deux fois avec les bons chemins
      calls = [
          call(os.path.join(data_path, 'CodeVilleClimat.csv'), sep=','),
          call(os.path.join(data_path, 'DataIds.csv'), sep=',')
      ]
      mock_read_csv.assert_has_calls(calls, any_order=True)


import os
from unittest.mock import patch, MagicMock, mock_open, call, ANY
import pandas as pd
from weather_utils.convert_to_one_csv import convert

def test_convert():
  data_path = '/fake_data_path'
  digest_path = os.path.join(data_path, 'digest')
  pandas_path = os.path.join(data_path, 'pandas')
  pandas_file_name = "weatherAUS.csv"
  pandas_file_path = os.path.join(pandas_path, pandas_file_name)

  # Données simulées pour merge_cvc_dids
  merged_cvc_dids = pd.DataFrame({
      'station_id': ['001'],
      'Location': ['Location1'],
      'data_id': ['DataID1']
  })

  # Liste simulée des fichiers dans digest_path
  csv_list = ['DataID1.202301.csv', 'DataID1.202302.csv']

  # Données simulées des CSV
  csv_data = pd.DataFrame({
      'Date': ['2023-01-01', '2023-01-02'],
      'MinTemp': [20.0, 18.5],
      'MaxTemp': [30.5, 29.0],
      'Rainfall': [0.0, 5.2],
      'Evaporation': [1.2, 1.5],
      'Sunshine': [10, 9],
      'WindGustDir': ['N', 'S'],
      'WindGustSpeed': [30, 35],
      'WindDir9am': ['N', 'NE'],
      'WindDir3pm': ['E', 'SE'],
      'WindSpeed9am': [15, 10],
      'WindSpeed3pm': [20, 15],
      'Humidity9am': [80, 85],
      'Humidity3pm': [60, 65],
      'Pressure9am': [1012, 1010],
      'Pressure3pm': [1008, 1007],
      'Cloud9am': [2, 3],
      'Cloud3pm': [4, 5],
      'Temp9am': [22, 21],
      'Temp3pm': [28, 27],
  })

  # Créer un DataFrame pour chaque fichier CSV
  csv_data_per_file = {
      os.path.join(digest_path, csv_file): csv_data for csv_file in csv_list
  }

  with patch('weather_utils.convert_to_one_csv.merge_cvc_dids') as mock_merge_cvc_dids, \
       patch('os.listdir') as mock_listdir, \
       patch('os.path.join', side_effect=lambda *args: "/".join(args)) as mock_path_join, \
       patch('pandas.read_csv') as mock_read_csv, \
       patch('pandas.DataFrame.to_csv') as mock_to_csv:

      # Configurer les mocks
      mock_merge_cvc_dids.return_value = merged_cvc_dids
      mock_listdir.return_value = csv_list
      # Simuler pandas.read_csv pour retourner csv_data pour chaque fichier
      def read_csv_side_effect(filepath_or_buffer, *args, **kwargs):
          return csv_data_per_file[filepath_or_buffer]
      mock_read_csv.side_effect = read_csv_side_effect

      # Appeler la fonction à tester
      convert(data_path)

      # Vérifier que merge_cvc_dids a été appelé
      mock_merge_cvc_dids.assert_called_once_with(data_path)
      # Vérifier que os.listdir a été appelé avec digest_path
      mock_listdir.assert_called_once_with(digest_path)
      # Vérifier que pandas.read_csv a été appelé pour chaque fichier CSV
      expected_calls = [
          call(
              filepath_or_buffer=os.path.join(digest_path, csv_file),
              sep=',',
              encoding='utf_8',
              header=None,
              names=ANY,
              index_col=None,
              skip_blank_lines=True
          )
          for csv_file in csv_list
      ]
      assert mock_read_csv.call_count == len(csv_list)
      mock_read_csv.assert_has_calls(expected_calls, any_order=True)
      # Vérifier que pandas.DataFrame.to_csv a été appelé pour enregistrer le fichier final
      mock_to_csv.assert_called_once_with(path_or_buf=pandas_file_path, index=False)